import { initializeApp } from "firebase/app";
import { getDatabase, ref, set } from "firebase/database";
const firebaseConfig = {
  apiKey: "AIzaSyAN3v5ub5WmkLb5vZSDSDTnjSL4Ey9Rbzs",
  authDomain: "iot-x-ml.firebaseapp.com",
  databaseURL: "https://iot-x-ml-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "iot-x-ml",
  storageBucket: "iot-x-ml.firebasestorage.app",
  messagingSenderId: "88329421908",
  appId: "1:88329421908:web:1afd3dd2b1beebb8ee99c1",
  measurementId: "G-2MC9BM69HY"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getDatabase();
const reference = ref (db, 'users/' +userId);