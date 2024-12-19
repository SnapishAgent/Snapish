const webpack = require("webpack");

module.exports = {
  devServer: {
    port: 8080, // 원하는 포트 번호로 변경
    proxy: {
      "/backend": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false),
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(true),
      }),
    ],
  },
};
