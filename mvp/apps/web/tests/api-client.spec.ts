import { expect, test } from "@playwright/test";
import { ApiError, createApiClient, getLastCorrelationId } from "@pol/api-client";

type Call = { url: string; method: string; headers: Record<string, string> };

function stubFetch(handler: (call: Call, init?: RequestInit) => Promise<Response>) {
  const original = globalThis.fetch;
  const calls: Call[] = [];
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const headers: Record<string, string> = {};
    new Headers(init?.headers).forEach((value, key) => {
      headers[key] = value;
    });
    const call = { url: String(input), method: init?.method ?? "GET", headers };
    calls.push(call);
    return handler(call, init);
  }) as typeof fetch;
  return {
    calls,
    restore: () => {
      globalThis.fetch = original;
    },
  };
}

function envelope(data: unknown, extraHeaders: Record<string, string> = {}) {
  return new Response(JSON.stringify({ success: true, data }), {
    status: 200,
    headers: { "Content-Type": "application/json", ...extraHeaders },
  });
}

test.describe("api client edge cases", () => {
  test("a 204 empty response raises PARSE_ERROR instead of returning undefined", async () => {
    const stub = stubFetch(async () => new Response(null, { status: 204 }));
    try {
      const client = createApiClient({ baseUrl: "http://stub" });
      const error = await client.get("/api/v1/whatever").catch((e: unknown) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).code).toBe("PARSE_ERROR");
      expect((error as ApiError).status).toBe(204);
    } finally {
      stub.restore();
    }
  });

  test("a cancelled request surfaces the abort, not a fake success", async () => {
    const stub = stubFetch(async () => {
      throw new DOMException("The operation was aborted.", "AbortError");
    });
    try {
      const client = createApiClient({ baseUrl: "http://stub" });
      const error = await client.get("/api/v1/slow").catch((e: unknown) => e);
      expect(error).toBeInstanceOf(DOMException);
      expect((error as DOMException).name).toBe("AbortError");
    } finally {
      stub.restore();
    }
  });

  test("a network failure propagates untouched and is not retried", async () => {
    const stub = stubFetch(async () => {
      throw new TypeError("fetch failed");
    });
    try {
      const client = createApiClient({ baseUrl: "http://stub" });
      const error = await client.post("/api/v1/baskets/current/items", { n: 1 }).catch(
        (e: unknown) => e,
      );
      expect(error).toBeInstanceOf(TypeError);
      expect(stub.calls).toHaveLength(1);
    } finally {
      stub.restore();
    }
  });

  test("401 triggers exactly one refresh retry with the new token", async () => {
    let refreshed = false;
    const stub = stubFetch(async (call) => {
      if (!refreshed) {
        refreshed = true;
        return new Response(
          JSON.stringify({ success: false, error: { code: "INVALID_ACCESS_TOKEN", message: "x", details: {} } }),
          { status: 401, headers: { "Content-Type": "application/json" } },
        );
      }
      expect(call.headers.authorization).toBe("Bearer new-token");
      return envelope({ ok: true });
    });
    try {
      let token = "old-token";
      const client = createApiClient({
        baseUrl: "http://stub",
        getAccessToken: () => token,
        onRefresh: async () => {
          token = "new-token";
          return true;
        },
      });
      await expect(client.get("/api/v1/orders")).resolves.toEqual({ ok: true });
      expect(stub.calls).toHaveLength(2);
    } finally {
      stub.restore();
    }
  });

  test("a failed refresh does not retry the request", async () => {
    const stub = stubFetch(async () =>
      new Response(
        JSON.stringify({ success: false, error: { code: "INVALID_ACCESS_TOKEN", message: "x", details: {} } }),
        { status: 401, headers: { "Content-Type": "application/json" } },
      ),
    );
    try {
      const signingOut: string[] = [];
      const client = createApiClient({
        baseUrl: "http://stub",
        onRefresh: async () => false,
        onUnauthorized: () => signingOut.push("1"),
      });
      const error = await client.get("/api/v1/orders").catch((e: unknown) => e);
      expect((error as ApiError).status).toBe(401);
      expect(stub.calls).toHaveLength(1);
      expect(signingOut).toHaveLength(1);
    } finally {
      stub.restore();
    }
  });


  test("concurrent requests keep correlation IDs attached to their own errors", async () => {
    let releaseSlow!: () => void;
    let markSlowJsonStarted!: () => void;
    const slowJsonGate = new Promise<void>((resolve) => {
      releaseSlow = resolve;
    });
    const slowJsonStarted = new Promise<void>((resolve) => {
      markSlowJsonStarted = resolve;
    });
    const stub = stubFetch(async (call) => {
      if (call.url.endsWith("/slow")) {
        const response = new Response(
          JSON.stringify({
            success: false,
            error: { code: "SLOW_FAILURE", message: "slow failure", details: {} },
          }),
          {
            status: 400,
            headers: {
              "Content-Type": "application/json",
              "X-Correlation-ID": "corr-slow",
            },
          },
        );
        const originalJson = response.json.bind(response);
        response.json = async () => {
          markSlowJsonStarted();
          await slowJsonGate;
          return originalJson();
        };
        return response;
      }
      return envelope({ ok: true }, { "X-Correlation-ID": "corr-fast" });
    });
    try {
      const client = createApiClient({ baseUrl: "http://stub" });
      const slowErrorPromise = client.get("/slow").then(
        () => null,
        (error: unknown) => error,
      );
      await slowJsonStarted;
      await client.get("/fast");
      releaseSlow();
      const slowError = await slowErrorPromise;
      expect(slowError).toBeInstanceOf(ApiError);
      expect((slowError as ApiError).correlationId).toBe("corr-slow");
      expect(getLastCorrelationId()).toBe("corr-fast");
    } finally {
      releaseSlow();
      stub.restore();
    }
  });

  test("correlation id from the response is exposed to error surfaces", async () => {
    const stub = stubFetch(async () =>
      envelope({ ok: true }, { "X-Correlation-ID": "corr-edge-1" }),
    );
    try {
      const client = createApiClient({ baseUrl: "http://stub" });
      await client.get("/api/v1/orders");
      expect(getLastCorrelationId()).toBe("corr-edge-1");
    } finally {
      stub.restore();
    }
  });
});
