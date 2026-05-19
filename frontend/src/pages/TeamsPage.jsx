import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTeams, createTeam, deleteTeam, addTeamMember, removeTeamMember } from '../api/teams'
import { getMembers } from '../api/workspace'
import AppLayout from '../components/layout/AppLayout'
import { Plus, Trash2, Users } from 'lucide-react'

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
}

function TeamCard({ team, members, onDelete, onAddMember, onRemoveMember }) {
  const [selectedUserId, setSelectedUserId] = useState('')

  const getMemberInfo = (userId) => {
    const m = members.find((m) => m.user_id === userId)
    return m?.user || null
  }

  const alreadyInTeam = (userId) => team.members.some((tm) => tm.user_id === userId)

  const handleAdd = () => {
    if (!selectedUserId) return
    onAddMember(team.id, selectedUserId)
    setSelectedUserId('')
  }

  return (
    <div className="bg-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Users size={18} className="text-indigo-400" />
          <h3 className="text-white font-semibold">{team.name}</h3>
          <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">
            {team.members.length} members
          </span>
        </div>
        <button
          onClick={() => onDelete(team.id, team.name)}
          className="text-gray-500 hover:text-red-400 transition-colors"
        >
          <Trash2 size={16} />
        </button>
      </div>

      <div className="space-y-2 mb-4">
        {team.members.length === 0 && (
          <p className="text-gray-500 text-sm">No members in this team yet.</p>
        )}
        {team.members.map((m) => {
          const userInfo = getMemberInfo(m.user_id)
          return (
            <div key={m.id} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-semibold">
                  {getInitials(userInfo?.name)}
                </div>
                <span className="text-gray-300 text-sm">
                  {userInfo?.name || userInfo?.email || m.user_id}
                </span>
              </div>
              <button
                onClick={() => onRemoveMember(team.id, m.user_id)}
                className="text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 size={13} />
              </button>
            </div>
          )
        })}
      </div>

      <div className="flex gap-2">
        <select
          value={selectedUserId}
          onChange={(e) => setSelectedUserId(e.target.value)}
          className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
        >
          <option value="">Select member to add...</option>
          {members
            .filter((m) => !alreadyInTeam(m.user_id))
            .map((m) => (
              <option key={m.user_id} value={m.user_id}>
                {m.user?.name || m.user?.email || m.user_id}
              </option>
            ))}
        </select>
        <button
          onClick={handleAdd}
          disabled={!selectedUserId}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white px-4 py-2 rounded-lg text-sm"
        >
          Add
        </button>
      </div>
    </div>
  )
}

export default function TeamsPage() {
  const queryClient = useQueryClient()
  const [showNewTeam, setShowNewTeam] = useState(false)
  const [newTeamName, setNewTeamName] = useState('')

  const { data: teamsData } = useQuery({ queryKey: ['teams'], queryFn: getTeams })
  const { data: membersData } = useQuery({ queryKey: ['members'], queryFn: getMembers })

  const teams = teamsData?.data || []
  const members = membersData?.data || []

  const createTeamMutation = useMutation({
    mutationFn: (data) => createTeam(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['teams'])
      setNewTeamName('')
      setShowNewTeam(false)
    },
  })

  const deleteTeamMutation = useMutation({
    mutationFn: deleteTeam,
    onSuccess: () => queryClient.invalidateQueries(['teams']),
  })

  const addTeamMemberMutation = useMutation({
    mutationFn: ({ teamId, userId }) => addTeamMember(teamId, { user_id: userId }),
    onSuccess: () => queryClient.invalidateQueries(['teams']),
  })

  const removeTeamMemberMutation = useMutation({
    mutationFn: ({ teamId, userId }) => removeTeamMember(teamId, userId),
    onSuccess: () => queryClient.invalidateQueries(['teams']),
  })

  const handleCreateTeam = () => {
    if (!newTeamName.trim()) return
    createTeamMutation.mutate({ name: newTeamName })
  }

  const handleDelete = (teamId, teamName) => {
    if (window.confirm(`Delete team "${teamName}"?`)) {
      deleteTeamMutation.mutate(teamId)
    }
  }

  const handleAddMember = (teamId, userId) => {
    addTeamMemberMutation.mutate({ teamId, userId })
  }

  const handleRemoveMember = (teamId, userId) => {
    removeTeamMemberMutation.mutate({ teamId, userId })
  }

  return (
    <AppLayout>
      <div className="max-w-3xl">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-white">Teams</h1>
          <button
            onClick={() => setShowNewTeam(!showNewTeam)}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm"
          >
            <Plus size={16} />
            New team
          </button>
        </div>

        {showNewTeam && (
          <div className="bg-gray-800 rounded-xl p-4 mb-6 flex gap-3">
            <input
              type="text"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Team name e.g. Engineering"
              className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
              autoFocus
              onKeyDown={(e) => e.key === 'Enter' && handleCreateTeam()}
            />
            <button
              onClick={handleCreateTeam}
              disabled={createTeamMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm"
            >
              {createTeamMutation.isPending ? 'Creating...' : 'Create'}
            </button>
            <button
              onClick={() => setShowNewTeam(false)}
              className="text-gray-400 px-3 py-2 rounded-lg text-sm hover:text-white"
            >
              Cancel
            </button>
          </div>
        )}

        {teams.length === 0 && !showNewTeam && (
          <div className="bg-gray-800 rounded-xl p-8 text-center">
            <Users size={32} className="text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No teams yet. Create one to get started.</p>
          </div>
        )}

        <div className="space-y-4">
          {teams.map((team) => (
            <TeamCard
              key={team.id}
              team={team}
              members={members}
              onDelete={handleDelete}
              onAddMember={handleAddMember}
              onRemoveMember={handleRemoveMember}
            />
          ))}
        </div>
      </div>
    </AppLayout>
  )
}