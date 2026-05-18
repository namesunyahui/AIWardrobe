import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Settings from '../components/Settings'

export default function SettingsPage() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const [isOpen, setIsOpen] = useState(true)

    const handleClose = () => {
        navigate('/profile')
    }

    const handleSave = () => {
        // 保存后的回调
    }

    return (
        <div className="min-h-screen bg-[var(--bg-primary)] max-w-md mx-auto">
            <Settings
                isOpen={isOpen}
                onClose={handleClose}
                onSave={handleSave}
            />
        </div>
    )
}