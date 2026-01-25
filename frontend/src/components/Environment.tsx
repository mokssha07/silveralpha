'use client'

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Points, PointMaterial } from '@react-three/drei'
import * as THREE from 'three'

export default function EnvironmentParticles() {
    const pointsRef = useRef<THREE.Points>(null)

    // Generate random particles
    const particles = useMemo(() => {
        const count = 1500
        const positions = new Float32Array(count * 3)
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 50
            positions[i * 3 + 1] = (Math.random() - 0.5) * 50
            positions[i * 3 + 2] = (Math.random() - 0.5) * 50
        }
        return positions
    }, [])

    useFrame((state, delta) => {
        if (!pointsRef.current) return
        pointsRef.current.rotation.y += delta * 0.05
        pointsRef.current.rotation.x += delta * 0.02
    })

    return (
        <group>
            <Points ref={pointsRef} positions={particles} stride={3} frustumCulled={false}>
                <PointMaterial
                    transparent
                    color="#ffffff"
                    size={0.05}
                    sizeAttenuation={true}
                    depthWrite={false}
                    blending={THREE.AdditiveBlending}
                />
            </Points>

            {/* Studio Lighting */}
            <ambientLight intensity={0.2} />
            <spotLight
                position={[10, 10, 10]}
                angle={0.15}
                penumbra={1}
                intensity={2}
                castShadow
            />
            <pointLight position={[-10, -10, -10]} intensity={0.5} color="#4444ff" />
            <rectAreaLight
                width={10}
                height={10}
                intensity={5}
                position={[0, 0, 5]}
                rotation={[0, Math.PI, 0]}
            />
        </group>
    )
}
