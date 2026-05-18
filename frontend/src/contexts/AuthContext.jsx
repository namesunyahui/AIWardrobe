import { createContext, useContext, useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [token, setToken] = useState(localStorage.getItem('access_token'))
    const [loading, setLoading] = useState(true)

    const isAuthenticated = !!token

    useEffect(() => {
        if (token) {
            fetchUserProfile()
        } else {
            setLoading(false)
        }
    }, [token])

    const fetchUserProfile = async () => {
        try {
            const response = await fetch(`${API_BASE}/auth/me`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (response.ok) {
                const userData = await response.json()
                setUser(userData)
            } else if (response.status === 401) {
                // Token 无效，清除并让用户重新登录
                console.log('Token 无效或已过期')
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                setToken(null)
                setUser(null)
                // 触发页面刷新以更新路由
                window.location.href = '/login'
            }
        } catch (error) {
            console.error('Failed to fetch user:', error)
        } finally {
            setLoading(false)
        }
    }

    const login = async (username, password) => {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })

        const data = await response.json()

        if (!response.ok) {
            throw new Error(data.detail || '登录失败')
        }

        // 保存 token
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        setToken(data.access_token)

        // 直接设置用户信息
        try {
            const userResponse = await fetch(`${API_BASE}/auth/me`, {
                headers: { Authorization: `Bearer ${data.access_token}` }
            })
            if (userResponse.ok) {
                const userData = await userResponse.json()
                setUser(userData)
            }
        } catch (e) {
            console.error('获取用户信息失败:', e)
        }

        return data
    }

    const register = async (userData) => {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        })

        const data = await response.json()

        if (!response.ok) {
            throw new Error(data.detail || '注册失败')
        }

        // 注册成功后自动登录
        return await login(userData.username, userData.password)
    }

    const logout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setToken(null)
        setUser(null)
        setLoading(false)
    }

    const updateProfile = async (profileData) => {
        const response = await fetch(`${API_BASE}/auth/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(profileData)
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || '更新失败')
        }

        const data = await response.json()
        setUser(data)
        return data
    }

    const changePassword = async (oldPassword, newPassword) => {
        const response = await fetch(`${API_BASE}/auth/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || '修改密码失败')
        }

        return await response.json()
    }

    return (
        <AuthContext.Provider value={{
            user,
            token,
            isAuthenticated,
            loading,
            login,
            register,
            logout,
            updateProfile,
            changePassword
        }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}