import axios from "axios";
let base_url = "http://127.0.0.1:8000/";
const apiConfig = axios.create({
  baseURL: base_url,
  headers: {
    "Content-Type": "application/json",
  },
});

export { apiConfig, base_url };
