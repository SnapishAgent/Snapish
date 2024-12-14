import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/Home.vue";
import Community from "./views/Community.vue";
import Profile from "./views/Profile.vue";
import FishResultNormal from "./views/FishResultNormal.vue";
import FishResultWarning from "./views/FishResultWarning.vue";
import WeatherSpecific from "./views/WeatherSpecific.vue";

// 라우트 설정
const routes = [
  {
    path: "/",
    name: "Home",
    component: Home, // 홈 컴포넌트
  },
  {
    path: "/community",
    name: "Community",
    component: Community, // 커뮤니티 컴포넌트
  },
  {
    path: "/weather-specific",
    name: "WeatherSpecific",
    component: WeatherSpecific, // 커뮤니티 컴포넌트
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile, // 프로필 컴포넌트
  },
  {
    path: "/fish-result-normal",
    name: "FishResultNormal",
    component: FishResultNormal,
    props: (route) => ({
      detections: route.query.detections,
      imageUrl: route.query.imageUrl,
    }),
  },
  {
    path: "/fish-result-warning",
    name: "FishResultWarning",
    component: FishResultWarning, // 물고기 경고 컴포넌트
  },
];

// 라우터 생성
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL), // 웹 히스토리 모드 사용
  routes, // 설정한 라우트들
});

export default router;
