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
    <div className="bg-gray-800 rounded-2xl p-6 w-full">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <Users size={24} className="text-indigo-400" />
          <h3 className="text-2xl font-semibold text-white">{team.name}</h3>
          <span className="text-base text-gray-500 bg-gray-700 px-3 py-1 rounded-full">
            {team.members.length} members
          </span>
        </div>
        <button
          onClick={() => onDelete(team.id, team.name)}
          className="text-gray-500 hover:text-red-400 transition-colors"
        >
          <Trash2 size={20} />
        </button>
      </div>

      <div className="space-y-3 mb-5">
        {team.members.length === 0 && (
          <p className="text-gray-500 text-base">No members in this team yet.</p>
        )}
        {team.members.map((m) => {
          const userInfo = getMemberInfo(m.user_id)
          return (
            <div key={m.id} className="flex items-center justify-between py-1">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  {getInitials(userInfo?.name)}
                </div>
                <span className="text-gray-200 text-base">
                  {userInfo?.name || userInfo?.email || m.user_id}
                </span>
              </div>
              <button
                onClick={() => onRemoveMember(team.id, m.user_id)}
                className="text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 size={16} />
              </button>
            </div>
          )
        })}
      </div>

      <div className="flex gap-3">
        <select
          value={selectedUserId}
          onChange={(e) => setSelectedUserId(e.target.value)}
          className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-xl text-base focus:outline-none"
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
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white px-6 py-3 rounded-xl text-base"
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

  return (
    <AppLayout>
      <div className="w-full max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">Teams</h1>
          <button
            onClick={() => setShowNewTeam(!showNewTeam)}
            className="flex items-center gap-3 bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-xl text-xl font-medium"
          >
            <Plus size={22} />
            New team
          </button>
        </div>

        {showNewTeam && (
          <div className="bg-gray-800 rounded-2xl p-6 mb-8 flex gap-4">
            <input
              type="text"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Team name e.g. Engineering"
              className="flex-1 bg-gray-700 text-white px-5 py-3 rounded-xl text-lg focus:outline-none"
              autoFocus
              onKeyDown={(e) => e.key === 'Enter' && handleCreateTeam()}
            />
            <button
              onClick={handleCreateTeam}
              disabled={createTeamMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl text-lg"
            >
              {createTeamMutation.isPending ? 'Creating...' : 'Create'}
            </button>
            <button
              onClick={() => setShowNewTeam(false)}
              className="text-gray-400 px-4 py-3 rounded-xl text-lg hover:text-white"
            >
              Cancel
            </button>
          </div>
        )}

        {teams.length === 0 && !showNewTeam && (
          <div className="bg-gray-800 rounded-2xl p-12 text-center w-full">
            <Users size={40} className="text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-xl">No teams yet. Create one to get started.</p>
          </div>
        )}

        <div className="space-y-5 w-full">
          {teams.map((team) => (
            <TeamCard
              key={team.id}
              team={team}
              members={members}
              onDelete={handleDelete}
              onAddMember={(teamId, userId) => addTeamMemberMutation.mutate({ teamId, userId })}
              onRemoveMember={(teamId, userId) => removeTeamMemberMutation.mutate({ teamId, userId })}
            />
          ))}
        </div>
      </div>
    </AppLayout>
  )
}