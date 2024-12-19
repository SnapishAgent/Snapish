module.exports = {
  root: true, // 이 설정 파일을 루트로 사용
  env: {
    node: true, // Node.js 환경을 사용
    "vue/setup-compiler-macros": true,
  },
  extends: ["plugin:vue/vue3-essential", "eslint:recommended"], // Vue3와 ESLint 권장 설정을 확장
  parserOptions: {
    parser: "babel-eslint", // Babel ESLint 파서를 사용
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off", // 프로덕션 환경에서는 console 사용을 경고
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off", // 프로덕션 환경에서는 debugger 사용을 경고
    "vue/multi-word-component-names": "off", // Vue 컴포넌트 이름이 여러 단어로 구성되지 않아도 허용
  },
  globals: {
    kakao: "readonly",
    defineProps: "readonly",
    defineEmits: "readonly",
  },
};
