import { createStore } from "vuex";
import { getCurrentLocation } from "../services/locationService";
import { fetchMulddae } from "../services/mulddaeService";

export default createStore({
  state: {
    currentlocation: null,
    loading: false,
    error: null,
    mulddae: null, // 물때 정보 추가
    mulddaeDate: null,
  },
  mutations: {
    setCurrentLocation(state, currentlocation) {
      state.currentlocation = currentlocation;
    },
    setLoading(state, isLoading) {
      state.loading = isLoading;
    },
    setError(state, error) {
      state.error = error;
    },
    setMulddae(state, mulddae) {
      state.mulddae = mulddae; // 물때 정보 업데이트
    },
  },
  actions: {
    async fetchMulddae({ commit }) {
      console.log("vuex : fetchMulddae action triggered.");
      commit("setLoading", true);
  
      try {
        // localStorage에서 데이터 확인
        const cachedMulddae = localStorage.getItem("mulddae");
        console.log(`cachedmulddae : ${cachedMulddae}`)
        const cachedDate = localStorage.getItem("mulddaeDate"); // 이전에 저장된 날짜
        const today = new Date().toISOString().split("T")[0]; // 오늘 날짜 (yyyy-mm-dd 형식)

        if (cachedMulddae && cachedDate === today) {
          // 저장된 데이터와 오늘 날짜가 같다면, 캐시된 데이터를 사용
          console.log("success : Loaded mulddae from localStorage.");
          commit("setMulddae", JSON.parse(cachedMulddae));
        } else {
          // 날짜가 다르거나 데이터가 없는 경우
          if (!cachedDate) {
            console.log("info : mulddaeDate is not found in localStorage, fetching new data.");
          } else if (cachedDate !== today) {
            console.log("info : Cached mulddae is outdated, fetching new data.");
          }
    
          const mulddaeData = await fetchMulddae(today);
          if (mulddaeData.error) {
            throw new Error(mulddaeData.error);
          }
    
          // 새 데이터와 날짜를 localStorage에 저장
          localStorage.setItem("mulddae", JSON.stringify(mulddaeData));
          localStorage.setItem("mulddaeDate", today); // 오늘 날짜를 저장
          commit("setMulddae", mulddaeData);
        }
      } catch (error) {
        console.error("error : Failed to fetch mulddae.", error);
        commit("setError", error.message || "Failed to fetch mulddae.");
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
  },
});
