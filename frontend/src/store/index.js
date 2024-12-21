import { createStore } from "vuex";
import axios from "@/axios"; // Ensure the correct path to axios.js
import { getCurrentLocation } from "../services/locationService";
import { fetchMulddae } from "../services/mulddaeService";

export default createStore({
  state: {
    // Existing state
    currentlocation: null,
    loading: false,
    error: null,
    mulddae: JSON.parse(localStorage.getItem('mulddae')) || null, // 물때 정보 추가
    mulddaeDate: null,

    // Authentication state
    isAuthenticated: !!localStorage.getItem("token"),
    user: JSON.parse(localStorage.getItem("user")) || { avatar: null },
    token: localStorage.getItem("token") || null,

    catches: JSON.parse(localStorage.getItem('catches')) || [], // Add catches state
    hotIssues: JSON.parse(localStorage.getItem('hotIssues')) || [],

    consent: {
      hasConsent: false,
      lastConsentDate: null
    },
    globalLoading: false,
    services: [],
  },
  mutations: {
    // Existing mutations
    setLoading(state, isLoading) {
      state.loading = isLoading;
    },
    setError(state, error) {
      state.error = error;
    },
    setMulddae(state, mulddae) {
      state.mulddae = mulddae; // 물때 정보 업데이트
      localStorage.setItem('mulddae', JSON.stringify(mulddae));
    },

    // Authentication mutations
    setAuth(state, payload) {
      state.isAuthenticated = payload.isAuthenticated;
      state.user = payload.user;
      state.token = payload.token;
    },
    clearAuth(state) {
      state.isAuthenticated = false;
      state.user = { avatar: null }; // Reset user to default state with no avatar
      state.token = null;
    },
    setCurrentLocation(state, currentlocation) {
      state.currentlocation = currentlocation;
    },

    setCatches(state, catches) {
      state.catches = catches;
      localStorage.setItem('catches', JSON.stringify(catches));
    },
    addCatch(state, newCatch) {
      state.catches.push(newCatch);
    },
    UPDATE_CATCH(state, updatedCatch) {
      const index = state.catches.findIndex((c) => c.id === updatedCatch.id); // Changed from '_id' to 'id'
      if (index !== -1) {
        state.catches.splice(index, 1, updatedCatch);
      }
    },
    SET_AVATAR(state, avatarUrl) {
      state.user.avatar = avatarUrl;
    },
    DELETE_CATCH(state, catchId) {
      state.catches = state.catches.filter(
        (catchItem) => catchItem.id !== catchId
      );
    },
    SET_USER(state, userData) {
      state.user = userData;
    },
    setUser(state, user) {
      state.user = user;
    },
    setHotIssues(state, issues) {
      state.hotIssues = issues;
      localStorage.setItem('hotIssues', JSON.stringify(issues));
    },
    SET_CONSENT(state, { hasConsent, lastConsentDate }) {
      state.consent = { hasConsent, lastConsentDate };
    },
    SET_GLOBAL_LOADING(state, isLoading) {
      state.globalLoading = isLoading;
    },
    SET_HOT_ISSUES(state, issues) {
      state.hotIssues = issues;
    },
    SET_SERVICES(state, services) {
      state.services = services;
    },
  },
  actions: {
    // Existing actions
    async fetchMulddae({ commit }) {
      console.log("vuex : fetchMulddae action triggered.");
      commit("setLoading", true);

      try {
        // localStorage에서 데이터 확인
        const cachedMulddae = localStorage.getItem("mulddae");
        const cachedDate = localStorage.getItem("mulddaeDate"); // 이전에 저장된 날짜
        const now = new Date();
        const today = now.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\. /g, '-').replace('.', ''); // 오늘 날짜 (yyyy-mm-dd 형식)

        // 캐시된 데이터와 날짜 확인
        if (cachedMulddae && cachedDate === today) {
          console.log("success : Loaded mulddae from localStorage.");
          commit("setMulddae", JSON.parse(cachedMulddae));
        } else {
          // 날짜가 다르거나 데이터가 없는 경우
          if (!cachedDate) {
            console.log(
              "info : mulddaeDate is not found in localStorage, fetching new data."
            );
          } else if (cachedDate !== today) {
            console.log(
              "info : Cached date is different from today, fetching new data."
            );
          }

          // 물때 정 API 호출
          const mulddaeData = await fetchMulddae(today);
          commit("setMulddae", mulddaeData);

          // 캐시에 저장 (오늘 날짜와 데이터)
          localStorage.setItem("mulddae", JSON.stringify(mulddaeData));
          localStorage.setItem("mulddaeDate", today);
        }

        // **유효성 검증 로직 추가**
        // 캐시된 날짜가 하루를 초과하면 자동 삭제
        const previousDate = cachedDate ? new Date(cachedDate) : null;
        if (previousDate && now.getDate() !== previousDate.getDate()) {
          console.log("info : Cached mulddae expired, clearing old data.");
          localStorage.removeItem("mulddae");
          localStorage.removeItem("mulddaeDate");
        }
      } catch (error) {
        console.error("Error fetching mulddae:", error);
        commit("setError", error);
      } finally {
        commit("setLoading", false);
      }
    },
    async fetchLocation({ commit }) {
      console.log("vuex : fetchLocation action triggered.");
      commit("setLoading", true);
      commit("setError", null);

      try {
        const { latitude, longitude } = await getCurrentLocation();

        if (latitude && longitude) {
          const currentloc = [latitude, longitude];
          console.log(`success : Fetch Location action ${currentloc}`);
          commit("setCurrentLocation", currentloc);
        } else {
          commit("setError", "No Location data found.");
        }
      } catch (error) {
        commit("setError", error);
      } finally {
        commit("setLoading", false);
      }
    },
    // Authentication actions
    async login({ commit }, { username, password }) {
      try {
        const response = await axios.post("/login", { username, password });
        const { token, user } = response.data; // Removed 'message'

        // 저장소와 로컬 스토리지 업데이트
        localStorage.setItem("token", token);
        localStorage.setItem("user", JSON.stringify(user));

        commit("setAuth", {
          isAuthenticated: true,
          user: user,
          token: token,
        });
      } catch (error) {
        console.error("Login error:", error);
        // Re-throw the error to be handled in the component
        throw error;
      }
    },
    async signup(_, { username, email, password }) {
      try {
        await axios.post("/signup", { username, email, password });
        // 회원가입 성공 후 추가 로직
      } catch (error) {
        console.error("Signup error:", error);
        throw error;
      }
    },
    logout({ commit }) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem('mulddae');
      localStorage.removeItem('catches');
      localStorage.removeItem('hotIssues');
      commit("clearAuth");
    },
    async fetchUserProfile({ commit }) {
      try {
        const response = await axios.get('http://localhost:5000/profile', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        commit('setUser', response.data);
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    },
    async updateProfile({ commit, state }, payload) {
      try {
        const response = await axios.put("/profile", payload);
        const updatedUser = response.data;
        localStorage.setItem("user", JSON.stringify(updatedUser));
        commit("setAuth", {
          isAuthenticated: true,
          user: updatedUser,
          token: state.token,
        });
      } catch (error) {
        console.error("Update profile error:", error);
        throw error;
      }
    },

    async fetchCatches({ commit, state }) {
      if (state.isAuthenticated) {
        try {
          const response = await axios.get("/catches", {
            headers: {
              Authorization: `Bearer ${state.token}`,
            },
          });
          const formattedCatches = response.data.map(item => ({
            ...item,
            catch_date: item.catch_date || new Date().toISOString().split('T')[0],
            weight_kg: item.weight_kg || null,
            length_cm: item.length_cm || null,
            latitude: item.latitude || null,
            longitude: item.longitude || null,
            memo: item.memo || ''
          }));
          commit("setCatches", formattedCatches);
        } catch (error) {
          commit("setError", error);
        }
      } else {
        commit("setCatches", []);
      }
    },
    async addCatch({ commit }, newCatch) {
      try {
        const response = await axios.post("/catches", newCatch);
        commit("addCatch", response.data);
      } catch (error) {
        console.error("Error adding catch:", error);
      }
    },
    async updateCatch({ commit }, updatedCatch) {
      try {
        if (!updatedCatch.id) {
          throw new Error('Catch ID is required');
        }
        const token = localStorage.getItem("token");
        const response = await axios.put(
          `/catches/${updatedCatch.id}`,
          updatedCatch,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        commit("UPDATE_CATCH", response.data);
        return response.data;
      } catch (error) {
        console.error(
          "Update catch error:",
          error.response ? error.response.data : error.message
        );
        throw error;
      }
    },
    async deleteCatch({ commit }, catchId) {
      try {
        const token = localStorage.getItem("token");
        await axios.delete(`http://localhost:5000/catches/${catchId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        commit("DELETE_CATCH", catchId);
      } catch (error) {
        console.error(
          "Delete catch error:",
          error.response ? error.response.data : error.message
        );
        throw error;
      }
    },
    updateAvatar({ commit }, avatarUrl) {
      commit("SET_AVATAR", avatarUrl);
    },
    async fetchServices({ commit }) {
      try {
        const response = await axios.get('/api/services');
        commit('SET_SERVICES', response.data);
      } catch (error) {
        console.error('Error fetching services:', error);
        // 기본 서비스 목록 사용
        const defaultServices = [
          {
            id: 1,
            name: "물때 정보",
            icon: "/icons/tide.png",
            route: "/map-location-service"
          },
          {
            id: 2,
            name: "날씨 정보",
            icon: "/icons/weather.png",
            route: "/map-location-service"
          },
          {
            id: 3,
            name: "내 기록",
            icon: "/icons/record.png",
            route: "/catches"
          },
          {
            id: 4,
            name: "커뮤니티",
            icon: "/icons/community.png",
            route: "/community"
          }
        ];
        commit('SET_SERVICES', defaultServices);
      }
    },
    updateUser({ commit }, userData) {
      commit('SET_USER', userData);
    },
    async fetchInitialData({ dispatch }) {
      try {
        await Promise.all([
          dispatch('fetchMulddae'),
          dispatch('fetchCatches'),
          dispatch('fetchHotIssues')
        ]);
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    },
    async checkConsent({ commit }) {
      try {
        console.log('Checking consent from backend...');
        const response = await axios.get('/api/consent/check', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        console.log('Consent response:', response.data);
        commit('SET_CONSENT', response.data);
        return response.data;
      } catch (error) {
        console.error('Error checking consent:', error);
        throw error;
      }
    },

    async updateConsent({ commit }, consentGiven) {
      try {
        const response = await axios.post('/api/consent', 
          { consent: consentGiven },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          }
        );
        commit('SET_CONSENT', {
          hasConsent: consentGiven,
          lastConsentDate: new Date().toISOString()
        });
        return response.data;
      } catch (error) {
        console.error('Error updating consent:', error);
        throw error;
      }
    },
    async createCatch({ commit }, catchData) {
      try {
        const response = await axios.post('/catches', catchData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        commit('addCatch', response.data);
        return response.data;
      } catch (error) {
        console.error('Error creating catch:', error);
        throw error;
      }
    },
    setGlobalLoading({ commit }, isLoading) {
      commit('SET_GLOBAL_LOADING', isLoading);
    },
    async fetchHotIssues({ commit }) {
      try {
        // 임시 데��터 사용 (실제 API 연동 전까지)
        const tempHotIssues = [
          {
            id: 1,
            title: '오늘의 조황 정보',
            content: '서해안 조황 정보입니다. 감성돔과 우럭이 잘 잡힙니다.',
            timestamp: new Date(),
            author: '낚시왕',
            imageUrl: 'https://picsum.photos/800/600?random=1'
          },
          {
            id: 2,
            title: '주말 날씨 전망',
            content: '주말 낚시하기 좋은 날씨입니다. 파고도 낮고 날씨도 맑습니다.',
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2시간 전
            author: '기상전문가',
            imageUrl: 'https://picsum.photos/800/600?random=2'
          },
          {
            id: 3,
            title: '금어기 안내',
            content: '올해 주요 어종별 금어기 정보를 확인하세요.',
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4시간 전
            author: '수산청',
            imageUrl: 'https://picsum.photos/800/600?random=3'
          }
        ];

        commit('SET_HOT_ISSUES', tempHotIssues);
        
        // 실제 API 연동 시 아래 코드 사용
        // const response = await axios.get('/backend/hot-issues');
        // commit('SET_HOT_ISSUES', response.data);
      } catch (error) {
        console.error('Error fetching hot issues:', error);
        throw error;
      }
    },
  },
  getters: {
    // Existing getters
    isAuthenticated(state) {
      return state.isAuthenticated;
    },
    user(state) {
      return state.user;
    },

    catches(state) {
      return state.catches;
    },
    isGlobalLoading: state => state.globalLoading,
    hotIssues: state => state.hotIssues,
    services: state => state.services,
  },
});
