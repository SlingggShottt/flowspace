import { useState } from 'react'
import Sidebar from './Sidebar'

export default function AppLayout({ children }) {
  return (
    <div className="flex bg-gray-950 min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6 bg-gray-950 min-h-screen overflow-x-auto transition-all duration-300 ml-72">
        {children}
      </main>
    </div>
  )
}