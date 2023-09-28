import React from 'react';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import LoginForm from "./components/login";
import RegisterForm from "./components/register";
import TestForm from "./components/test";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="login" element={<LoginForm />} />
          <Route path="register" element={<RegisterForm />} />
          <Route path="test" element={<TestForm />} />
      </Routes>
    </BrowserRouter>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);