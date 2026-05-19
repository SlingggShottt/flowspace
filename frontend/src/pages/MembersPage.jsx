import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getMembers, inviteMember, removeMember } from '../api/workspace'
import AppLayout from '../components/layout/AppLayout'
import { UserPlus, Trash2 } from 'lucide-react'

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
}

export default function MembersPage() {
  const queryClient = useQueryClient()
  const [showInvite, setShowInvite] = useState(false)
  const [inviteForm, setInviteForm] = useState({ email: '', role: 'member' })
  const [error, setError] = useState('')

  const { data: membersData } = useQuery({ queryKey: ['members'], queryFn: getMembers })
  const members = membersData?.data || []

  const inviteMutation = useMutation({
    mutationFn: inviteMember,
    onSuccess: () => {
      queryClient.invalidateQueries(['members'])
      setShowInvite(false)
      setInviteForm({ email: '', role: 'member' })
      setError('')
    },
    onError: (err) => setError(err.response?.data?.detail || 'Failed to invite'),
  })

  const removeMemberMutation = useMutation({
    mutationFn: removeMember,
    onSuccess: () => queryClient.invalidateQueries(['members']),
  })

  return (
    <AppLayout>
      <div className="max-w-3xl">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-white">Members</h1>
          <button
            onClick={() => setShowInvite(!showInvite)}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm"
          >
            <UserPlus size={16} />
            Invite member
          </button>
        </div>

        {showInvite && (
          <div className="bg-gray-800 rounded-xl p-4 mb-6">
            {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
            <div className="flex gap-3 flex-wrap">
              <input
                type="email"
                value={inviteForm.email}
                onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                placeholder="Email address"
                className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none min-w-48"
              />
              <select
                value={inviteForm.role}
                onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                className="bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
              >
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
              <button
                onClick={() => inviteMutation.mutate(inviteForm)}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm"
              >
                Invite
              </button>
            </div>
          </div>
        )}

        <div className="bg-gray-800 rounded-xl divide-y divide-gray-700">
          {members.length === 0 && (
            <p className="text-gray-400 text-sm p-4">No members yet.</p>
          )}
          {members.map((member) => (
            <div key={member.id} className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  {getInitials(member.user?.name)}
                </div>
                <div>
                  <p className="text-white text-sm font-medium">
                    {member.user?.name || 'Unknown'}
                  </p>
                  <p className="text-gray-400 text-xs">{member.user?.email}</p>
                </div>
                <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full capitalize">
                  {member.role}
                </span>
              </div>
              <button
                onClick={() => removeMemberMutation.mutate(member.id)}
                className="text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  )
}