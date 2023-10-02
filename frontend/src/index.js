import React from 'react';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import LoginForm from "./components/login";
import RegisterForm from "./components/register";
import TestForm from "./components/test";
import ProfileComponent from "./components/profile";
import LogOut from "./components/signout";
import StreamersComponent from "./components/streamers";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="login" element={<LoginForm />} />
          <Route path="register" element={<RegisterForm />} />
          <Route path="test" element={<TestForm />} />
          <Route path="profile" element={<ProfileComponent />} />
          <Route path="logout" element={<LogOut />} />
          <Route path="streamers" element={<StreamersComponent />} />
      </Routes>
    </BrowserRouter>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);