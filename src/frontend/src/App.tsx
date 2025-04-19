import { useState } from 'react'
import Header from './components/Header'
import SearchBar from './components/SearchBar'
import './App.css'

function App() {
  return (
    <>
      <header className='title-container'>
        <div className='header-container'>
          <Header />
        </div>
      </header>
      <header className='title-container'>
        <div className='header-container'>
          <SearchBar />
        </div>
      </header>
    </>
    
  )
}

export default App
