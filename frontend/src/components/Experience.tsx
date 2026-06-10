'use client'

import { useState, useEffect, useCallback } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { Environment, OrbitControls } from '@react-three/drei'
import { motion, AnimatePresence } from 'framer-motion'
import gsap from 'gsap'
import Coin from './Coin'
import EnvironmentParticles from './Environment'
import Globe from './Globe'
import GlobeUI from './GlobeUI'
import TypingText from './TypingText'

export interface GlobeNode {
    id: number
    region: string
    lat: number
    lon: number
    direction: 'up' | 'down' | 'neutral'
    sentiment: 1 | -1 | 0
    narrative: string
    pressure: number
    size: number
    stability: number
}

export interface NodeDetail {
    id: number
    narrative: string
    narrative_score: number
    trust_level: string
    action_state: 'WATCH' | 'BUY' | 'SELL'
    sentiment: string
    time_series: Array<{ time: number | string; value: number }>
    indicators: {
        size: number
        velocity: number
        stability: number
        sources: number
    }
    metrics: {
        pressure: number
        direction: string
        cluster_size: number
    }
    horizon: string
    sourcesList: string[]
}

export interface SelectedGlobeData extends Omit<NodeDetail, 'sentiment'> {
    heading: string
    trust: string
    action: 'WATCH' | 'BUY' | 'SELL'
    change: number
    direction: GlobeNode['direction']
    sentiment: GlobeNode['sentiment']
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8000/api'

// Camera Manager to handle smooth transitions and resets between views
function CameraController({ view, isFocused }: { view: 'landing' | 'repository', isFocused: boolean }) {
    const { camera } = useThree()

    useEffect(() => {
        if (view === 'landing') {
            gsap.to(camera.position, { z: 10, x: 0, y: 0, duration: 1.5, ease: 'power3.inOut' })
        } else if (view === 'repository') {
            if (isFocused) {
                gsap.to(camera.position, { z: 2.8, duration: 1.2, ease: "power2.inOut" })
            } else {
                gsap.to(camera.position, { z: 4, duration: 1.2, ease: "power2.inOut" })
            }
        }
    }, [view, isFocused, camera])

    return null
}

export default function Experience() {
    const [view, setView] = useState<'landing' | 'repository'>('landing')
    const [selectedGlobeData, setSelectedGlobeData] = useState<SelectedGlobeData | null>(null)

    const handleSelectGlobeNode = useCallback(async (node: GlobeNode) => {
        try {
            const res = await fetch(`${API_BASE}/node/${node.id}/`)
            const json = await res.json() as { status: string; data?: NodeDetail }

            if (json.status === 'success' && json.data) {
                setSelectedGlobeData({
                    ...json.data,
                    heading: json.data.narrative,
                    trust: json.data.trust_level,
                    action: json.data.action_state,
                    change: json.data.narrative_score,
                    sentiment: node.sentiment,
                    direction: node.direction,
                    horizon: json.data.horizon,
                    sourcesList: json.data.sourcesList,
                })
            }
        } catch (err) {
            console.error('Failed to fetch node detail:', err)
        }
    }, [])

    const [deckKey, setDeckKey] = useState(0)

    const handleEnterRepository = useCallback(() => {
        window.scrollTo({ top: 0, behavior: 'instant' })
        setView('repository')
    }, [])

    const handleBackToLanding = useCallback(() => {
        window.scrollTo({ top: 0, behavior: 'instant' })
        setSelectedGlobeData(null)
        setView('landing')
        setDeckKey(k => k + 1)
    }, [])

    return (
        <main className="bg-black text-white w-full min-h-screen selection:bg-zinc-500/30">

            {/* 1. The 3D Scene */}
            <div
                className={`fixed inset-0 w-full h-screen ${view !== 'landing' ? 'pointer-events-auto' : 'pointer-events-none'}`}
                style={{ zIndex: 0 }}
            >
                <Canvas
                    shadows
                    camera={{ position: [0, 0, 10], fov: 35 }}
                    gl={{ antialias: true, alpha: true }}
                >
                    <color attach="background" args={['#000']} />

                    <CameraController view={view} isFocused={!!selectedGlobeData} />

                    {view === 'repository' && (
                        <OrbitControls
                            enableDamping
                            autoRotate={!selectedGlobeData}
                            autoRotateSpeed={0.3}
                            makeDefault
                        />
                    )}

                    <AnimatePresence>
                        {view === 'landing' ? (
                            <group key="landing-scene">
                                <EnvironmentParticles />
                                <Coin key={deckKey} />
                                <Environment preset="studio" resolution={2048} />
                                <spotLight position={[10, 20, 10]} intensity={50} angle={0.12} penumbra={1} castShadow />
                                <spotLight position={[-15, 10, 5]} intensity={30} color="#ffffff" angle={0.2} />
                                <pointLight position={[0, -5, 5]} intensity={20} color="#ffffff" />
                                <rectAreaLight position={[0, 0, 8]} width={10} height={10} intensity={10} color="#fff" />
                            </group>
                        ) : (
                            <group key="repository-scene">
                                <Globe
                                    onSelect={handleSelectGlobeNode}
                                    isFocused={!!selectedGlobeData}
                                />
                                <ambientLight intensity={1.0} />
                                <pointLight position={[10, 10, 10]} intensity={2} color="#21ED8D" />
                                <pointLight position={[-10, -10, 10]} intensity={1} color="#fff" />
                            </group>
                        )}
                    </AnimatePresence>
                </Canvas>
            </div>

            {/* 2. The UI Layer */}
            <AnimatePresence mode="wait">
                {view === 'landing' ? (
                    <motion.div
                        key="landing-ui"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0, y: -100 }}
                        transition={{ duration: 0.8, ease: "easeInOut" }}
                        className="relative z-10 w-full overflow-x-hidden"
                    >
                        <section className="h-screen w-full flex items-center justify-center text-center px-10">
                            <div className="max-w-3xl">
                                <h1 className="text-[12vw] md:text-8xl font-black tracking-tighter leading-none text-luxury">
                                    Silver Alpha
                                </h1>
                                <p className="mt-6 text-zinc-500 font-medium tracking-[0.4em] uppercase text-[10px] md:text-xs">
                                    Built with precision
                                </p>
                            </div>
                        </section>

                        <section className="h-screen w-full flex items-center px-10 md:px-24">
                            <div className="max-w-xl">
                                <TypingText
                                    text="Interactive Experience"
                                    className="text-5xl md:text-7xl font-bold tracking-tight text-silver leading-none uppercase"
                                />
                                <TypingText
                                    text="Explore predictions by clicking, not reading complex charts."
                                    className="mt-8 text-zinc-400 font-medium text-lg leading-relaxed max-w-md"
                                    delay={0.5}
                                />
                            </div>
                        </section>

                        <section className="h-screen w-full flex items-center justify-end px-10 md:px-24 text-right">
                            <div className="max-w-xl w-full flex flex-col items-end">
                                <TypingText
                                    text="INNOVATIVE SOLUTIONS"
                                    className="text-5xl md:text-7xl font-bold tracking-tight text-luxury leading-none uppercase justify-end w-full"
                                />
                                <TypingText
                                    text="Compressing scattered data into a single actionable insight."
                                    className="mt-8 text-zinc-400 font-medium text-lg leading-relaxed max-w-md ml-auto justify-end w-full"
                                    delay={0.5}
                                />
                            </div>
                        </section>

                        <section className="h-screen w-full flex flex-col items-center justify-center text-center px-10">
                            <h2 className="text-[12vw] font-black tracking-tighter text-white opacity-[0.03] uppercase select-none">
                                LAUNCH NOW
                            </h2>
                            <button
                                onClick={handleEnterRepository}
                                className="mt-12 px-12 py-5 border border-zinc-700/50 rounded-full hover:bg-white hover:text-black transition-all duration-500 font-bold tracking-[0.2em] uppercase text-xs backdrop-blur-md pointer-events-auto cursor-pointer"
                            >
                                Discover
                            </button>
                            <div className="mt-20 text-zinc-800 text-[10px] tracking-[0.5em] uppercase">2026 SILVER ALPHA</div>
                        </section>
                    </motion.div>
                ) : (
                    <motion.div
                        key="repository-ui"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 1 }}
                        className="fixed inset-0 z-20 pointer-events-none"
                    >
                        <GlobeUI
                            selectedData={selectedGlobeData}
                            onClose={() => setSelectedGlobeData(null)}
                        />

                        <div className="absolute bottom-10 left-10 w-full flex justify-start pointer-events-none">
                            <button
                                onClick={handleBackToLanding}
                                className="px-10 py-4 border border-neon/30 rounded-full bg-black/40 text-neon hover:bg-neon hover:text-black transition-all duration-500 font-bold tracking-[0.2em] uppercase text-xs backdrop-blur-md pointer-events-auto cursor-pointer shadow-[0_0_30px_rgba(33,237,141,0.1)]"
                            >
                                Return to Deck
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </main>
    )
}
