'use client'

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh, CanvasTexture, LinearFilter, MathUtils } from 'three'
import { Float } from '@react-three/drei'

function seededRandom(seed: number) {
    const x = Math.sin(seed) * 10000
    return x - Math.floor(x)
}

export default function Coin() {
    const meshRef = useRef<Mesh>(null)
    const smoothedScroll = useRef(0) // Persistent smoothed value

    // Professional Minimalist 4K Texture
    const coinTexture = useMemo(() => {
        if (typeof document === 'undefined') return null
        const canvas = document.createElement('canvas')
        const size = 4096
        canvas.width = size
        canvas.height = size
        const ctx = canvas.getContext('2d')
        if (!ctx) return null

        // 1. Machined Metal Base
        ctx.fillStyle = '#9aa1a9'
        ctx.fillRect(0, 0, size, size)

        ctx.strokeStyle = 'rgba(255,255,255,0.06)'
        ctx.lineWidth = 2
        for (let i = 0; i < 1500; i++) {
            const y = seededRandom(i + 1) * size
            ctx.beginPath()
            ctx.moveTo(0, y)
            ctx.lineTo(size, y)
            ctx.stroke()
        }

        // 2. High-Precision Rim
        ctx.strokeStyle = '#ffffff'
        ctx.lineWidth = 15
        ctx.beginPath()
        ctx.arc(size / 2, size / 2, size * 0.48, 0, Math.PI * 2)
        ctx.stroke()

        const drawMinimalText = (text: string, x: number, y: number, radius: number, startAngle: number, kerning: number, color: string, fontSize: number) => {
            ctx.font = `500 ${fontSize}px sans-serif`
            ctx.fillStyle = color
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'

            const characters = text.split('')
            const totalAngle = (characters.length - 1) * kerning

            characters.forEach((char, i) => {
                const angle = startAngle - (totalAngle / 2) + (i * kerning)
                ctx.save()
                ctx.translate(x + Math.cos(angle) * radius, y + Math.sin(angle) * radius)
                ctx.rotate(angle + Math.PI / 2)
                ctx.fillText(char, 0, 0)
                ctx.restore()
            })
        }

        drawMinimalText('SILVER ALPHA · PRECISION ASSET', size / 2, size / 2, size * 0.45, -Math.PI / 2, 0.045, '#fff', size * 0.022)
        drawMinimalText('QUANTUM SERIES · MODEL 001 · 24', size / 2, size / 2, size * 0.45, Math.PI / 2, 0.04, '#fff', size * 0.018)

        const drawMonogram = (color: string, ox: number, oy: number) => {
            ctx.save()
            ctx.translate(size / 2 + ox, size / 2 + oy)
            ctx.strokeStyle = color
            ctx.lineWidth = 90
            ctx.lineJoin = 'round'
            ctx.lineCap = 'round'

            ctx.beginPath()
            ctx.moveTo(0, -380)
            ctx.lineTo(380, 250)
            ctx.lineTo(-380, 250)
            ctx.closePath()
            ctx.stroke()

            ctx.beginPath(); ctx.moveTo(-180, 0); ctx.lineTo(180, 0); ctx.stroke()

            ctx.lineWidth = 25
            ctx.beginPath(); ctx.arc(0, 0, 580, 0, Math.PI * 2); ctx.stroke()

            ctx.restore()
        }

        ctx.shadowColor = 'rgba(0,0,0,0.4)'
        ctx.shadowBlur = 30
        drawMonogram('#ffffff', 0, 0)

        const texture = new CanvasTexture(canvas)
        texture.anisotropy = 16
        texture.minFilter = LinearFilter
        return texture
    }, [])

    useFrame((state, delta) => {
        if (!meshRef.current) return

        // 1. Get Target Scroll
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
        const scrollTop = typeof window !== 'undefined' ? window.scrollY : 0
        const targetScroll = scrollHeight > 0 ? scrollTop / scrollHeight : 0

        // 2. LERP (Linear Interpolation) for Buttery Smoothness
        smoothedScroll.current = MathUtils.damp(smoothedScroll.current, targetScroll, 2.2, delta)
        const scrollOffset = smoothedScroll.current

        // 3. Apply Transformations
        meshRef.current.rotation.x = scrollOffset * (Math.PI * 6) + (Math.PI / 2)
        meshRef.current.position.z = scrollOffset * 8.5 - 1.5
        meshRef.current.position.y = Math.sin(scrollOffset * Math.PI) * 0.5

        // Continuous organic drift
        meshRef.current.rotation.z += delta * 0.05
    })

    return (
        <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.4}>
            <mesh ref={meshRef}>
                <cylinderGeometry args={[2, 2, 0.22, 128, 5]} />
                <meshStandardMaterial
                    color="#ffffff"
                    metalness={1.0}
                    roughness={0.03}
                    bumpMap={coinTexture}
                    bumpScale={0.08}
                    envMapIntensity={6.0}
                />
            </mesh>
        </Float>
    )
}
