import React from 'react'
import { NavLink } from 'react-router-dom'

export default function Nav() {
  const today = new Date().toLocaleDateString('en-GB', {
    day: '2-digit', month: 'long', year: 'numeric'
  })

  return (
    <header className="masthead">
      <div className="masthead-inner">
        {/* Logo */}
        <div className="mast-title">
          404AnomalyNotFound
          <small>SIH Problem · 25172 · ATLAS SkillTech University</small>
        </div>

        {/* Nav links */}
        <nav className="mast-nav">
          <NavLink to="/" className={({isActive}) => isActive ? 'active' : ''}>
            <span className="num">§01</span>Dashboard
          </NavLink>
          <NavLink to="/assistant" className={({isActive}) => isActive ? 'active' : ''}>
            <span className="num">§02</span>AI Assistant
          </NavLink>
          <NavLink to="/about" className={({isActive}) => isActive ? 'active' : ''}>
            <span className="num">§03</span>About
          </NavLink>
          <a href="https://github.com/rishitladdha" target="_blank" rel="noopener noreferrer">
            <span className="num">↗</span>GitHub
          </a>
        </nav>

        {/* Meta */}
        <div className="mast-meta">
          <strong>Rishit Laddha</strong><br />
          {today}
        </div>
      </div>
    </header>
  )
}
