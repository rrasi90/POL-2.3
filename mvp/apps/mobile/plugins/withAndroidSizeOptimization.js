const { withGradleProperties } = require("expo/config-plugins");

module.exports = function withAndroidSizeOptimization(config) {
  return withGradleProperties(config, (config) => {
    const values = new Map([
      ["android.enableMinifyInReleaseBuilds", "true"],
      ["android.enableShrinkResourcesInReleaseBuilds", "true"],
      ["expo.gif.enabled", "false"],
      ["expo.webp.enabled", "false"],
    ]);

    const existing = new Map(
      config.modResults.map((item) => [item.key, item.value]),
    );

    for (const [key, value] of values) existing.set(key, value);

    config.modResults = [...existing.entries()].map(([key, value]) => ({
      type: "property",
      key,
      value,
    }));

    return config;
  });
};
