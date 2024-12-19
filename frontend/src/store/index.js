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
    mulddae: null, // 물때 정보 추가
    mulddaeDate: null,

    // Authentication state
    isAuthenticated: !!localStorage.getItem("token"),
    user: JSON.parse(localStorage.getItem("user")) || { avatar: null },
    token: localStorage.getItem("token") || null,

    catches: [], // Add catches state
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

          // 물때 정보 API 호출
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
      commit("clearAuth");
    },
    async fetchUserProfile({ commit, state }) {
      try {
        const response = await axios.get("/profile", {
          headers: {
            Authorization: `Bearer ${state.token}`,
          },
        });
        const userData = response.data;
        commit("setAuth", {
          isAuthenticated: true,
          user: userData,
          token: state.token,
        });
      } catch (error) {
        console.error("Fetch user profile error:", error);
        commit("clearAuth");
        throw error;
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
        // Fetch catches from the database for authenticated users
        try {
          const response = await axios.get("/catches", {
            headers: {
              Authorization: `Bearer ${state.token}`,
            },
          });
          commit("setCatches", response.data);
        } catch (error) {
          commit("setError", error);
        }
      } else {
        // Handle catches for unauthenticated users if necessary
        // For example, you might fetch from local storage or handle differently
        commit("setCatches", []); // Or appropriate handling
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
        const token = localStorage.getItem("token");
        const response = await axios.put(
          `http://localhost:5000/catches/${updatedCatch.id}`,
          updatedCatch,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
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
    fetchServices({ commit }) {
      // Define the fetchServices action
      // Example implementation:
      return fetch("http://localhost:5000/api/services")
        .then((response) => response.json())
        .then((data) => {
          commit("setServices", data);
        });
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
  },
});
