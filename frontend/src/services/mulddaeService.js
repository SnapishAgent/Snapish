import axios from 'axios';

const apiBaseUrl = process.env.VUE_APP_MULDDAE_URL;

export async function fetchMulddae(date) {
  console.log(`js : ${ date }`)
  try {
    const response = await axios.post(apiBaseUrl, new URLSearchParams({ nowdate: date }).toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching mulddae data:", error);
    return { error: error.message };
  }
}
