// Vue 애플리케이션을 생성하기 위해 createApp 함수를 import 합니다.
import { createApp } from "vue";

// App 컴포넌트를 import 합니다.
import App from "./App.vue";

// 라우터 설정을 import 합니다.
import router from "./router";

// Vuex 스토어 설정을 import 합니다.
import store from "./store";

// Tailwind CSS 파일을 import 합니다.
import "./assets/tailwind.css";

// Vue 애플리케이션을 생성하고, 스토어와 라우터를 사용하도록 설정한 후, #app 엘리먼트에 마운트합니다.
const app = createApp(App);

// Example: Initialize Vue without '_id' references

app
  .use(store) // Vuex 스토어를 사용하도록 설정합니다.
  .use(router) // 라우터를 사용하도록 설정합니다.
  .mount("#app"); // #app 엘리먼트에 애플리케이션을 마운트합니다.
