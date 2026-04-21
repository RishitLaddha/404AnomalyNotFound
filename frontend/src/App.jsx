import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Nav from './components/Nav'
import Dashboard from './pages/Dashboard'
import Assistant from './pages/Assistant'
import About from './pages/About'

export default function App() {
  return (
    <div>
      <Nav />
      <Routes>
        <Route path="/"          element={<Dashboard />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/about"     element={<About />} />
      </Routes>
    </div>
  )
}
