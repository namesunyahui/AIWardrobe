import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { AlertTriangle, X } from 'lucide-react'

export default function ConfirmDialog() {
    const { t } = useTranslation()
    const [dialog, setDialog] = useState(null)
    const [isVisible, setIsVisible] = useState(false)

    const openDialog = useCallback((detail) => {
        setDialog(detail)
        setIsVisible(true)
    }, [])

    const closeDialog = useCallback(() => {
        setIsVisible(false)
        setTimeout(() => setDialog(null), 300)
    }, [])

    const handleConfirm = () => {
        if (dialog?.onConfirm) {
            dialog.onConfirm()
        }
        closeDialog()
    }

    useEffect(() => {
        const handler = (event) => openDialog(event.detail)
        window.addEventListener('show-confirm', handler)
        return () => window.removeEventListener('show-confirm', handler)
    }, [openDialog])

    if (!dialog) return null

    const {
        title,
        message,
        confirmText,
        cancelText,
        type = 'warning'
    } = dialog

    // 使用 settings 命名空间下的翻译（因为 cancel/confirm 在 settings 对象内）
    const translatedConfirm = t('settings.confirm')
    const translatedCancel = t('settings.cancel')

    const typeStyles = {
        warning: {
            icon: 'text-amber-500',
            bg: 'bg-amber-50 dark:bg-amber-900/20',
            border: 'border-amber-200 dark:border-amber-800',
            confirmBtn: 'bg-amber-500 hover:bg-amber-600 text-white',
        },
        danger: {
            icon: 'text-red-500',
            bg: 'bg-red-50 dark:bg-red-900/20',
            border: 'border-red-200 dark:border-red-800',
            confirmBtn: 'bg-red-500 hover:bg-red-600 text-white',
        },
        info: {
            icon: 'text-blue-500',
            bg: 'bg-blue-50 dark:bg-blue-900/20',
            border: 'border-blue-200 dark:border-blue-800',
            confirmBtn: 'bg-blue-500 hover:bg-blue-600 text-white',
        },
    }

    const styles = typeStyles[type] || typeStyles.warning

    return (
        <div
            className={`
                fixed inset-0 z-[60] flex items-center justify-center p-4
                transition-all duration-300
                ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}
            `}
        >
            {/* 遮罩层 */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={cancelText !== '删除' ? closeDialog : undefined}
            />

            {/* 对话框 */}
            <div
                className={`
                    relative w-full max-w-sm bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl
                    border ${styles.border} overflow-hidden
                    transform transition-all duration-300
                    ${isVisible ? 'scale-100 translate-y-0' : 'scale-95 translate-y-4'}
                `}
            >
                {/* 关闭按钮 */}
                <button
                    onClick={closeDialog}
                    className="absolute top-3 right-3 p-1 rounded-lg text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                >
                    <X size={18} />
                </button>

                {/* 内容 */}
                <div className="p-6">
                    <div className={`flex items-center justify-center w-12 h-12 rounded-full ${styles.bg} mx-auto mb-4`}>
                        <AlertTriangle size={24} className={styles.icon} />
                    </div>

                    <h3 className="text-lg font-bold text-zinc-900 dark:text-zinc-100 text-center mb-2">
                        {title}
                    </h3>

                    <p className="text-sm text-zinc-500 dark:text-zinc-400 text-center leading-relaxed">
                        {message}
                    </p>
                </div>

                {/* 按钮 */}
                <div className="flex gap-3 px-6 pb-6">
                    <button
                        onClick={closeDialog}
                        className="flex-1 px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 font-medium hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
                    >
                        {translatedCancel}
                    </button>
                    <button
                        onClick={handleConfirm}
                        className={`flex-1 px-4 py-2.5 rounded-xl font-medium transition-colors ${styles.confirmBtn}`}
                    >
                        {translatedConfirm}
                    </button>
                </div>
            </div>
        </div>
    )
}

export function showConfirm(options) {
    return new Promise((resolve) => {
        const handler = (event) => {
            const { confirmed } = event.detail
            window.removeEventListener('confirm-result', resultHandler)
            resolve(confirmed)
        }
        const resultHandler = (event) => handler(event)

        window.addEventListener('confirm-result', resultHandler)

        window.dispatchEvent(new CustomEvent('show-confirm', {
            detail: {
                ...options,
                onConfirm: () => {
                    window.dispatchEvent(new CustomEvent('confirm-result', { detail: { confirmed: true } }))
                }
            }
        }))
    })
}