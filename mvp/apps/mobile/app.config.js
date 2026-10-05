const base = require("./app.json").expo;
const variant = (process.env.POL_APP_VARIANT || "retailer").toLowerCase();
const isVendor = variant === "vendor";

const vendorLogo = "./assets/vendor-logo.png";
const retailerIcon = "./assets/icon.png";

module.exports = {
  ...base,
  name: isVendor ? "پل بنکدار" : "پل بازار",
  slug: isVendor ? "pol-vendor" : "pol-market",
  version: "1.0.0",
  icon: isVendor ? vendorLogo : retailerIcon,
  userInterfaceStyle: "automatic",
  extra: { ...(base.extra || {}), appVariant: isVendor ? "vendor" : "retailer", dataMode: (process.env.EXPO_PUBLIC_DATA_MODE || "live").toLowerCase() },
  plugins: [
    ...(base.plugins || []),
    ["expo-font", {
      fonts: [
        "./assets/fonts/Vazirmatn-Regular.ttf",
        "./assets/fonts/Vazirmatn-SemiBold.ttf",
        "./assets/fonts/Vazirmatn-Bold.ttf",
      ],
    }],
    "./plugins/withAndroidSizeOptimization.js",
  ],
  android: {
    ...(base.android || {}),
    package: isVendor ? "ir.pol.vendor" : "ir.pol.market",
    icon: isVendor ? vendorLogo : base.android?.icon,
    versionCode: 100,
    adaptiveIcon: isVendor
      ? {
          backgroundColor: "#F7F9FC",
          foregroundImage: vendorLogo,
        }
      : base.android?.adaptiveIcon,
    splash: isVendor
      ? {
          backgroundColor: "#F7F9FC",
          image: vendorLogo,
          resizeMode: "contain",
        }
      : base.android?.splash,
  },
};
