import { useState } from 'react'
import { Bell, Check, CheckCheck } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getNotifications, markAsRead, markAllAsRead } from '../../api/notifications'
import { useNavigate } from 'react-router-dom'

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const { data: notifData } = useQuery({
    queryKey: ['notifications'],
    queryFn: getNotifications,
    refetchInterval: 30000,
  })

  const notifications = notifData?.data || []
  const unreadCount = notifications.filter((n) => !n.is_read).length

  const markReadMutation = useMutation({
    mutationFn: markAsRead,
    onSuccess: () => queryClient.invalidateQueries(['notifications']),
  })

  const markAllReadMutation = useMutation({
    mutationFn: markAllAsRead,
    onSuccess: () => queryClient.invalidateQueries(['notifications']),
  })

  const handleClick = (notification) => {
    if (!notification.is_read) {
      markReadMutation.mutate(notification.id)
    }
    setIsOpen(false)
    if (notification.project_id) {
      navigate(`/board/${notification.project_id}`)
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative text-gray-400 hover:text-white transition-colors p-2 bg-gray-800 rounded-xl"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center font-medium">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-full mt-2 w-80 bg-gray-800 rounded-xl shadow-xl z-50 overflow-hidden border border-gray-700">
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
              <p className="text-white font-medium">Notifications</p>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button
                    onClick={() => markAllReadMutation.mutate()}
                    className="text-gray-400 hover:text-white"
                    title="Mark all as read"
                  >
                    <CheckCheck size={16} />
                  </button>
                )}
                <button
                  onClick={() => { setIsOpen(false); navigate('/notifications') }}
                  className="text-xs text-indigo-400 hover:underline"
                >
                  See all
                </button>
              </div>
            </div>

            {notifications.length === 0 ? (
              <p className="text-gray-400 text-sm p-4">No notifications yet</p>
            ) : (
              <div className="max-h-80 overflow-y-auto">
                {notifications.slice(0, 10).map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => handleClick(notification)}
                    className={`flex items-start gap-3 px-4 py-3 border-b border-gray-700 last:border-0 cursor-pointer hover:bg-gray-700 transition-colors ${
                      !notification.is_read ? 'bg-indigo-900/10' : ''
                    }`}
                  >
                    <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                      !notification.is_read ? 'bg-indigo-500' : 'bg-gray-600'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm ${!notification.is_read ? 'text-white font-medium' : 'text-gray-300'}`}>
                        {notification.title}
                      </p>
                      {notification.body && (
                        <p className="text-gray-400 text-xs mt-0.5 truncate">{notification.body}</p>
                      )}
                      <p className="text-gray-600 text-xs mt-0.5">
                        {new Date(notification.created_at).toLocaleString()}
                      </p>
                    </div>
                    {!notification.is_read && (
                      <button
                        onClick={(e) => { e.stopPropagation(); markReadMutation.mutate(notification.id) }}
                        className="text-gray-500 hover:text-indigo-400 flex-shrink-0"
                      >
                        <Check size={14} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}