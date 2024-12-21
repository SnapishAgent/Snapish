import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:5000", // Ensure this matches your backend's base URL
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true, // Include credentials in requests
});

// 이미지 압축 함수 추가
export const compressImage = async (file, maxWidth = 1024) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ratio = maxWidth / img.width;
        canvas.width = maxWidth;
        canvas.height = img.height * ratio;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
          resolve(new File([blob], file.name, {
            type: 'image/jpeg',
            lastModified: Date.now()
          }));
        }, 'image/jpeg', 0.8);
      };
    };
  });
};

// 이미지 업로드 전 압축 처리
instance.interceptors.request.use(async (config) => {
  if (config.data instanceof FormData && config.data.get('image')) {
    const file = config.data.get('image');
    if (file.type.startsWith('image/')) {
      const compressedFile = await compressImage(file);
      config.data.set('image', compressedFile);
    }
  }
  return config;
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
