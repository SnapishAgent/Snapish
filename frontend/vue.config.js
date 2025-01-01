const webpack = require("webpack");
const baseUrl = process.env.VUE_APP_BASE_URL;

module.exports = {
  devServer: {
    port: 81, // 원하는 포트 번호로 변경
    proxy: {
      "/": {
        target: baseUrl,
        changeOrigin: true,
        ws: false,
      },
      "/backend": {
        target: baseUrl,
        changeOrigin: true,
        ws: false,
      },
      "/api": {
        target: baseUrl,
        changeOrigin: true,
        ws: false,
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
  chainWebpack: (config) => {
    // 이미지 최적화
    config.module
      .rule("images")
      .use("image-webpack-loader")
      .loader("image-webpack-loader")
      .options({
        mozjpeg: {
          progressive: true,
          quality: 65,
        },
        optipng: {
          enabled: false,
        },
        pngquant: {
          quality: [0.65, 0.9],
          speed: 4,
        },
        gifsicle: {
          interlaced: false,
        },
        webp: {
          quality: 75,
        },
      });

    // 코드 스플리팅
    config.optimization.splitChunks({
      chunks: "all",
      minSize: 20000,
      maxSize: 250000,
    });
  },

  pwa: {
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true,
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/api/,
          handler: "NetworkFirst",
          options: {
            networkTimeoutSeconds: 5,
            cacheName: "api-cache",
            expiration: {
              maxEntries: 50,
              maxAgeSeconds: 5 * 60, // 5분
            },
          },
        },
      ],
    },
  },
};
