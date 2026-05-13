import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { ChevronDown, Check, X } from 'lucide-react'

export default function MultiSelect({
    label,
    icon: Icon,
    name,
    value = [],
    options = [],
    onChange,
    placeholder = '请选择',
    translateKey = null
}) {
    const { t } = useTranslation()
    const [isOpen, setIsOpen] = useState(false)
    const wrapperRef = useRef(null)

    const translateOption = (option) => {
        if (translateKey) {
            const translated = t(`${translateKey}${option}`)
            return translated === `${translateKey}${option}` ? option : translated
        }
        return option
    }

    const getOriginalKey = (val) => {
        if (translateKey) {
            for (const opt of options) {
                if (translateOption(opt) === val) {
                    return opt
                }
            }
        }
        return val
    }

    useEffect(() => {
        function handleClickOutside(event) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const isSelected = (option) => {
        for (const v of value) {
            if (v === option || translateOption(option) === v || getOriginalKey(v) === option) {
                return true
            }
        }
        return false
    }

    const handleToggle = (option) => {
        if (isSelected(option)) {
            const newValue = value.filter(v =>
                v !== option && translateOption(option) !== v && getOriginalKey(v) !== option
            )
            onChange({ target: { name, value: newValue } })
        } else {
            const newValue = [...value, translateOption(option)]
            onChange({ target: { name, value: newValue } })
        }
    }

    const handleClear = (e) => {
        e.stopPropagation()
        onChange({ target: { name, value: [] } })
    }

    return (
        <div className="space-y-1.5" ref={wrapperRef}>
            <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                {Icon && <Icon className="text-accent" size={16} />}
                {label}
            </label>
            <div className="relative">
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    className="input-field appearance-none text-left flex items-center justify-between pr-10"
                >
                    <span className={value.length > 0 ? 'text-zinc-900 dark:text-zinc-100' : 'text-zinc-400'}>
                        {value.length > 0 ? `${value.length} 已选择` : placeholder}
                    </span>
                    <ChevronDown
                        size={18}
                        className={`text-zinc-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                    />
                </button>

                {value.length > 0 && (
                    <button
                        type="button"
                        onClick={handleClear}
                        className="absolute right-8 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600"
                    >
                        <X size={16} />
                    </button>
                )}

                {isOpen && (
                    <div className="absolute z-50 w-full mt-1 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                        {options.map((option) => (
                            <button
                                key={option}
                                type="button"
                                onClick={() => handleToggle(option)}
                                className={`w-full px-4 py-2.5 text-left flex items-center justify-between hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors ${
                                    isSelected(option) ? 'bg-accent/10 text-accent' : 'text-zinc-700 dark:text-zinc-200'
                                }`}
                            >
                                <span>{translateOption(option)}</span>
                                {isSelected(option) && <Check size={16} />}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {value.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                    {value.map((v) => (
                        <span
                            key={v}
                            className="inline-flex items-center gap-1 px-2 py-1 bg-accent/10 text-accent text-xs rounded-lg"
                        >
                            {v}
                            <button
                                type="button"
                                onClick={() => handleToggle(getOriginalKey(v))}
                                className="hover:text-blue-700"
                            >
                                <X size={12} />
                            </button>
                        </span>
                    ))}
                </div>
            )}
        </div>
    )
}