import { useEffect, useState, useCallback } from 'react'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'

const TOAST_TYPES = {
    success: { icon: CheckCircle, color: 'text-green-600 dark:text-green-400', bg: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800' },
    error: { icon: XCircle, color: 'text-red-600 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800' },
    warning: { icon: AlertTriangle, color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800' },
    info: { icon: Info, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800' }
}

function Toast({ toast, onRemove }) {
    const [isLeaving, setIsLeaving] = useState(false)
    const config = TOAST_TYPES[toast.type] || TOAST_TYPES.info
    const Icon = config.icon

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsLeaving(true)
            setTimeout(() => onRemove(toast.id), 300)
        }, toast.duration || 3000)

        return () => clearTimeout(timer)
    }, [toast.id, toast.duration, onRemove])

    const handleClose = () => {
        setIsLeaving(true)
        setTimeout(() => onRemove(toast.id), 300)
    }

    return (
        <div
            className={`
                flex items-start gap-3 p-3 rounded-lg border shadow-lg
                ${config.bg} ${config.color}
                transition-all duration-300 ease-out
                ${isLeaving ? 'opacity-0 translate-x-4' : 'opacity-100 translate-x-0'}
                max-w-sm w-full
            `}
        >
            <Icon size={20} className="flex-shrink-0 mt-0.5" />
            <p className="text-sm font-medium flex-1 text-zinc-800 dark:text-zinc-100">{toast.message}</p>
            <button
                onClick={handleClose}
                className="flex-shrink-0 p-0.5 hover:bg-black/5 dark:hover:bg-white/10 rounded transition-colors"
            >
                <X size={16} />
            </button>
        </div>
    )
}

export default function ToastContainer() {
    const [toasts, setToasts] = useState([])

    const addToast = useCallback((toast) => {
        const id = Date.now() + Math.random()
        setToasts(prev => [...prev, { ...toast, id }])
    }, [])

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id))
    }, [])

    useEffect(() => {
        const handleShowToast = (event) => {
            const { type, message } = event.detail
            addToast({ type: type || 'info', message })
        }

        window.addEventListener('show-toast', handleShowToast)
        return () => window.removeEventListener('show-toast', handleShowToast)
    }, [addToast])

    if (toasts.length === 0) return null

    return (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-2 pointer-events-none">
            {toasts.map(toast => (
                <div key={toast.id} className="pointer-events-auto">
                    <Toast toast={toast} onRemove={removeToast} />
                </div>
            ))}
        </div>
    )
}

export function showToast(type, message) {
    window.dispatchEvent(new CustomEvent('show-toast', {
        detail: { type, message }
    }))
}