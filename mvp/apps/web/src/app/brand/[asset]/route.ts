import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";

const ASSETS = {
  corporate: "pol company logo.png",
  market: "لوگو پل برای مغازه داران.png",
  vendor: "لوگو پل برای بنکدار.png",
} as const;

export const revalidate = 31536000;

type AssetKey = keyof typeof ASSETS;

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ asset: string }> },
) {
  const { asset } = await params;

  if (!(asset in ASSETS)) {
    return new NextResponse("Not Found", { status: 404 });
  }

  const fileName = ASSETS[asset as AssetKey];
  const filePath = path.join(process.cwd(), "logo", fileName);

  try {
    const data = await readFile(filePath);
    return new NextResponse(new Uint8Array(data), {
      status: 200,
      headers: {
        "Content-Type": "image/png",
        "Cache-Control": "public, max-age=31536000, immutable",
      },
    });
  } catch {
    return new NextResponse("Brand asset unavailable", { status: 404 });
  }
}
