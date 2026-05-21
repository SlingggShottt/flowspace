import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getNotifications, markAsRead, markAllAsRead } from '../api/notifications'
import AppLayout from '../components/layout/AppLayout'
import { Bell, Check, CheckCheck } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function NotificationsPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const { data: notifData, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: getNotifications,
  })

  const notifications = notifData?.data || []

  const markReadMutation = useMutation({
    mutationFn: markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications'])
      queryClient.invalidateQueries(['unread-count'])
    },
  })

  const markAllReadMutation = useMutation({
    mutationFn: markAllAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications'])
      queryClient.invalidateQueries(['unread-count'])
    },
  })

  const handleClick = (notification) => {
    if (!notification.is_read) {
      markReadMutation.mutate(notification.id)
    }
    if (notification.project_id) {
      navigate(`/board/${notification.project_id}`)
    }
  }

  return (
    <AppLayout>
      <div className="w-full max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">Notifications</h1>
          {notifications.some((n) => !n.is_read) && (
            <button
              onClick={() => markAllReadMutation.mutate()}
              className="flex items-center gap-2 text-gray-400 hover:text-white text-sm"
            >
              <CheckCheck size={16} />
              Mark all as read
            </button>
          )}
        </div>

        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : notifications.length === 0 ? (
          <div className="bg-gray-800 rounded-2xl p-12 text-center">
            <Bell size={40} className="text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No notifications yet</p>
          </div>
        ) : (
          <div className="bg-gray-800 rounded-2xl divide-y divide-gray-700">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                onClick={() => handleClick(notification)}
                className={`flex items-start gap-4 px-6 py-4 cursor-pointer hover:bg-gray-700 transition-colors ${
                  !notification.is_read ? 'bg-indigo-900/10' : ''
                }`}
              >
                <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                  !notification.is_read ? 'bg-indigo-500' : 'bg-gray-600'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${!notification.is_read ? 'text-white' : 'text-gray-300'}`}>
                    {notification.title}
                  </p>
                  {notification.body && (
                    <p className="text-gray-400 text-sm mt-0.5">{notification.body}</p>
                  )}
                  <p className="text-gray-600 text-xs mt-1">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                </div>
                {!notification.is_read && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      markReadMutation.mutate(notification.id)
                    }}
                    className="text-gray-500 hover:text-indigo-400 flex-shrink-0"
                    title="Mark as read"
                  >
                    <Check size={16} />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}