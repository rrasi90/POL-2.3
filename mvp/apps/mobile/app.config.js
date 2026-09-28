const base = require("./app.json").expo;
const variant = (process.env.POL_APP_VARIANT || process.env.EXPO_PUBLIC_APP_VARIANT || "retailer").toLowerCase();
const isVendor = variant === "vendor";

module.exports = {
  ...base,
  name: isVendor ? "پل بنکدار" : "پل بازار",
  slug: isVendor ? "pol-vendor" : "pol-market",
  version: "1.0.0",
  extra: { ...(base.extra || {}), appVariant: isVendor ? "vendor" : "retailer" },
  android: {
    ...(base.android || {}),
    package: isVendor ? "ir.pol.vendor" : "ir.pol.market",
    versionCode: 100,
  },
};
