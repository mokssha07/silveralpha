'use client'
import { useRef, useEffect, useState, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useTexture } from '@react-three/drei'
import type { GlobeNode } from './Experience'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8000/api'
const API_URL = `${API_BASE}/globe/nodes/`
const NEON_GREEN = '#21ED8D'

function seededRandom(seed: number) {
    const x = Math.sin(seed) * 10000
    return x - Math.floor(x)
}

const NewsBeam = ({ item, onSelect }: { item: GlobeNode; onSelect: (data: GlobeNode) => void }) => {
    const beamRef = useRef<THREE.Mesh>(null)
    const circleRef = useRef<THREE.Mesh>(null)

    const isPositive = item.direction === 'up'
    const color = isPositive ? 0x00ff88 : item.direction === 'down' ? 0xff3333 : 0xb8c1cc
    const height = 0.22

    // ✅ CORRECT LAT/LON → XYZ
    const latRad = THREE.MathUtils.degToRad(item.lat)
    const lonRad = THREE.MathUtils.degToRad(item.lon)

    const position = useMemo(() => {
        const x = Math.cos(latRad) * Math.sin(lonRad)
        const y = Math.sin(latRad)
        const z = Math.cos(latRad) * Math.cos(lonRad)
        return new THREE.Vector3(x, y, z)
    }, [latRad, lonRad])

    const geometry = useMemo(() => {
        const g = new THREE.CylinderGeometry(0, 0.012, height, 4)
        g.translate(0, height / 2, 0)
        return g
    }, [])

    const quaternion = useMemo(() => {
        const q = new THREE.Quaternion()
        q.setFromUnitVectors(new THREE.Vector3(0, 1, 0), position.clone().normalize())
        return q
    }, [position])

    useFrame(({ clock }) => {
        const t = clock.getElapsedTime()
        const opacity = 0.6 + Math.sin(t * 4 + item.lat) * 0.3
        if (beamRef.current) (beamRef.current.material as THREE.MeshBasicMaterial).opacity = opacity
        if (circleRef.current) (circleRef.current.material as THREE.MeshBasicMaterial).opacity = opacity
    })

    return (
        <group>
            <mesh
                ref={beamRef}
                position={position}
                quaternion={quaternion}
                geometry={geometry}
                onClick={(e) => {
                    e.stopPropagation()
                    onSelect(item)
                }}
            >
                <meshBasicMaterial color={color} transparent />
            </mesh>

            <mesh
                ref={circleRef}
                position={position.clone().multiplyScalar(1.002)}
                onUpdate={(self) => self.lookAt(0, 0, 0)}
                onClick={(e) => {
                    e.stopPropagation()
                    onSelect(item)
                }}
            >
                <circleGeometry args={[0.025, 32]} />
                <meshBasicMaterial color={color} transparent side={THREE.DoubleSide} />
            </mesh>
        </group>
    )
}

export default function Globe({
    onSelect,
    isFocused,
}: {
    onSelect: (data: GlobeNode) => void
    isFocused: boolean
}) {
    const worldRef = useRef<THREE.Group>(null)
    const earthTexture = useTexture(
        'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg'
    )

    const [newsData, setNewsData] = useState<GlobeNode[]>([])
    const [locked, setLocked] = useState(false)

    const targetRotation = useRef({ x: 0, y: 0 })

    // ⭐ STARFIELD (UNCHANGED)
    const starPositions = useMemo(() => {
        const count = 12000
        const positions = new Float32Array(count * 3)

        for (let i = 0; i < count; i++) {
            const radius = 15 + seededRandom(i * 3 + 1) * 25
            const theta = seededRandom(i * 3 + 2) * Math.PI * 2
            const phi = Math.acos(2 * seededRandom(i * 3 + 3) - 1)

            positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
            positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
            positions[i * 3 + 2] = radius * Math.cos(phi)
        }

        return positions
    }, [])

    useEffect(() => {
        fetch(API_URL)
            .then(res => res.json())
            .then((json: { status: string; data?: GlobeNode[] }) => {
                if (json.status === 'success') setNewsData(json.data ?? [])
            })
            .catch(console.error)
    }, [])

    const handleSelect = (item: GlobeNode) => {
        const latRad = THREE.MathUtils.degToRad(item.lat)
        const lonRad = THREE.MathUtils.degToRad(item.lon)

        targetRotation.current.y = Math.PI - lonRad
        targetRotation.current.x = latRad

        setLocked(true)
        onSelect(item)
    }

    useFrame(() => {
        if (!worldRef.current) return

        if (!locked && !isFocused) {
            worldRef.current.rotation.y += 0.001
        } else {
            worldRef.current.rotation.y = THREE.MathUtils.lerp(
                worldRef.current.rotation.y,
                targetRotation.current.y,
                0.12
            )

            worldRef.current.rotation.x = THREE.MathUtils.lerp(
                worldRef.current.rotation.x,
                targetRotation.current.x,
                0.12
            )
        }

        worldRef.current.position.set(0, 0, 0)
        worldRef.current.rotation.z = 0
    })

    return (
        <group>
            {/* ⭐ Starfield */}
            <points>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[starPositions, 3]} />
                </bufferGeometry>
                <pointsMaterial
                    color="#21ED8D"
                    size={0.035}
                    transparent
                    opacity={0.9}
                    depthWrite={false}
                />
            </points>

            <group ref={worldRef}>
                {/* 🌍 EARTH — CORRECT TEXTURE ALIGNMENT */}
                <mesh rotation={[0, Math.PI / 2, 0]}>
                    <sphereGeometry args={[1, 64, 64]} />
                    <meshBasicMaterial
                        color={NEON_GREEN}
                        transparent
                        opacity={0.85}
                        alphaMap={earthTexture}
                    />
                </mesh>

                <mesh>
                    <sphereGeometry args={[0.98, 64, 64]} />
                    <meshBasicMaterial color="#000" />
                </mesh>

                {newsData.map((item, i) => (
                    <NewsBeam key={i} item={item} onSelect={handleSelect} />
                ))}
            </group>
        </group>
    )
}
