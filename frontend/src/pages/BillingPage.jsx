import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getBillingInfo, createOrder, verifyPayment, downgradeToFree } from '../api/billing'
import AppLayout from '../components/layout/AppLayout'
import { Check, Zap, Building2 } from 'lucide-react'

const PLANS = [
  {
    key: 'free',
    name: 'Free',
    price: '₹0',
    period: 'forever',
    color: 'gray',
    features: [
      'Up to 3 projects',
      'Up to 5 members',
      'Basic kanban board',
      'Task management',
    ],
  },
  {
    key: 'pro',
    name: 'Pro',
    price: '₹999',
    period: 'per month',
    color: 'indigo',
    features: [
      'Up to 10 projects',
      'Unlimited members',
      'Advanced kanban board',
      'Team management',
      'Priority support',
      'File attachments',
    ],
  },
  {
    key: 'enterprise',
    name: 'Enterprise',
    price: '₹2,999',
    period: 'per month',
    color: 'purple',
    features: [
      'Everything in Pro',
      'Custom integrations',
      'Dedicated support',
      'SLA guarantee',
      'Audit logs',
      'Advanced analytics',
    ],
  },
]

export default function BillingPage() {
  const queryClient = useQueryClient()

  const { data: billingData, isLoading } = useQuery({
    queryKey: ['billing'],
    queryFn: getBillingInfo,
  })

  const billing = billingData?.data

  const downgradeMutation = useMutation({
    mutationFn: downgradeToFree,
    onSuccess: () => queryClient.invalidateQueries(['billing']),
  })

  const handleUpgrade = async (planKey) => {
    if (planKey === 'free') {
      if (window.confirm('Downgrade to free plan? Some features will be limited.')) {
        downgradeMutation.mutate()
      }
      return
    }

    try {
      const orderRes = await createOrder({ plan: planKey })
      const order = orderRes.data

      const options = {
        key: billing.razorpay_key_id,
        amount: order.amount,
        currency: order.currency,
        name: 'Flowspace',
        description: `Upgrade to ${planKey} plan`,
        order_id: order.order_id,
        handler: async (response) => {
          await verifyPayment({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
            plan: planKey,
          })
          queryClient.invalidateQueries(['billing'])
          alert('Payment successful! Plan upgraded.')
        },
        theme: { color: '#6366f1' },
      }

      const rzp = new window.Razorpay(options)
      rzp.open()
    } catch (err) {
      alert(err.response?.data?.detail || 'Payment failed')
    }
  }

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-96">
          <p className="text-gray-400 text-lg">Loading billing info...</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="w-full max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Billing</h1>
          <p className="text-gray-400 text-lg">
            Current plan:{' '}
            <span className="text-indigo-400 font-semibold capitalize">
              {billing?.current_plan}
            </span>
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {PLANS.map((plan) => {
            const isCurrent = billing?.current_plan === plan.key
            const isPopular = plan.key === 'pro'

            return (
              <div
                key={plan.key}
                className={`bg-gray-800 rounded-2xl p-8 flex flex-col relative ${
                  isCurrent ? 'ring-2 ring-indigo-500' : ''
                }`}
              >
                {isPopular && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-sm px-4 py-1 rounded-full">
                    Most Popular
                  </span>
                )}

                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    {plan.key === 'pro' && <Zap size={20} className="text-indigo-400" />}
                    {plan.key === 'enterprise' && <Building2 size={20} className="text-purple-400" />}
                    <h3 className="text-xl font-bold text-white">{plan.name}</h3>
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    <span className="text-gray-400">{plan.period}</span>
                  </div>
                </div>

                <ul className="space-y-3 flex-1 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-gray-300">
                      <Check size={16} className="text-green-400 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleUpgrade(plan.key)}
                  disabled={isCurrent}
                  className={`w-full py-3 rounded-xl text-lg font-medium transition-colors ${
                    isCurrent
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : plan.key === 'free'
                      ? 'bg-gray-700 hover:bg-gray-600 text-white'
                      : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                  }`}
                >
                  {isCurrent ? 'Current Plan' : plan.key === 'free' ? 'Downgrade' : 'Upgrade'}
                </button>
              </div>
            )
          })}
        </div>

        <div className="bg-gray-800 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Current Plan Limits</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded-xl p-4">
              <p className="text-gray-400 text-sm mb-1">Max Projects</p>
              <p className="text-white text-2xl font-bold">
                {billing?.limits.max_projects === 999 ? 'Unlimited' : billing?.limits.max_projects}
              </p>
            </div>
            <div className="bg-gray-700 rounded-xl p-4">
              <p className="text-gray-400 text-sm mb-1">Max Members</p>
              <p className="text-white text-2xl font-bold">
                {billing?.limits.max_members === 999 ? 'Unlimited' : billing?.limits.max_members}
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}