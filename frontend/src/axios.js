import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:5000", // Ensure this matches your backend's base URL
  withCredentials: true, // Include credentials in requests
});

// Add a request interceptor to include the token
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default instance;
