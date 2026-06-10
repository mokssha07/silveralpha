'use client'

import React, { useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { SelectedGlobeData } from './Experience'

interface IndicatorProps {
    label: string
    value: number
    color: string
}

const IndicatorBar = ({ label, value, color }: IndicatorProps) => (
    <div className="flex flex-col gap-2.5 mb-5">
        <div className="flex justify-between items-center px-1">
            <span className="text-[14px] uppercase tracking-[0.25em] text-white/50 font-bold">{label}</span>
            <span className="text-[14px] font-bold" style={{ color }}>{value}%</span>
        </div>
        <div className="h-[10px] w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 1.2, ease: "circOut" }}
                className="h-full rounded-full"
                style={{ backgroundColor: color, boxShadow: `0 0 15px ${color}66` }}
            />
        </div>
    </div>
)

function seededRandom(seed: number) {
    const x = Math.sin(seed) * 10000
    return x - Math.floor(x)
}

export default function GlobeUI({ selectedData, onClose }: { selectedData: SelectedGlobeData | null, onClose: () => void }) {
    const sentiment = selectedData?.sentiment ?? 0
    const isBullish = sentiment === 1
    const themeColor = isBullish ? '#21ED8D' : sentiment === -1 ? '#ff3333' : '#b8c1cc'

    const indicators = {
        size: selectedData?.indicators?.size ?? 0,
        velocity: selectedData?.indicators?.velocity ?? 0,
        stability: selectedData?.indicators?.stability ?? 0,
        sources: selectedData?.indicators?.sources ?? 0
    }

    const sourcesList: string[] = Array.isArray(selectedData?.sourcesList)
        ? selectedData.sourcesList
        : []
    const selectedId = selectedData?.id ?? 0

    const graphData = useMemo(() => {
        const points = 100
        let lastClose = 50
        const data = []

        for (let i = 0; i < points; i++) {
            const open = lastClose
            const movement = (seededRandom(i + selectedId * 101) - 0.5) * 6
            const close = Math.max(10, Math.min(90, open + movement))

            data.push({
                x: (i / (points - 1)) * 100,
                y: close
            })

            lastClose = close
        }
        return data
    }, [selectedId])

    if (!selectedData) return null

    return (
        <div className="absolute inset-0 pointer-events-none z-20 font-mono">
            <AnimatePresence>
                <motion.div
                    initial={{ x: 600, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: 600, opacity: 0 }}
                    transition={{ type: 'spring', damping: 30, stiffness: 100 }}
                    className="absolute top-[3%] bottom-[3%] right-10 w-[600px] p-10 text-white pointer-events-auto overflow-y-auto thin-scrollbar"
                    style={{
                        background: 'rgba(0, 0, 0, 0.28)',
                        borderRadius: '16px',
                        backdropFilter: 'blur(9.4px)',
                        border: '1px solid rgba(0, 0, 0, 0.55)'
                    }}
                >
                    <button
                        onClick={onClose}
                        className="absolute top-10 right-10 text-white/30 hover:text-white"
                    >
                        ✕
                    </button>

                    <h3 className="text-3xl font-bold uppercase mb-4">
                        {selectedData.heading ?? 'Unknown Narrative'}
                    </h3>

                    <div className="flex items-center gap-6 mb-8">
                        <div className="text-5xl" style={{ color: themeColor }}>
                            {isBullish ? '▲' : sentiment === -1 ? '▼' : '■'}
                        </div>
                        <div className="text-6xl font-black">
                            {selectedData.change ?? '0.0'}%
                        </div>
                    </div>

                    <div className="mb-10">
                        <span className="uppercase tracking-widest text-white/50">Trust Level</span>
                        <div className="text-xl font-black" style={{ color: themeColor }}>
                            {selectedData.trust ?? 'Unknown'}
                        </div>
                    </div>

                    <div className="mb-12">
                        <svg width="100%" height="200" viewBox="0 0 100 100" preserveAspectRatio="none">
                            <path
                                d={`M 0 100 ${graphData.map(p => `L ${p.x} ${100 - p.y}`).join(' ')} L 100 100 Z`}
                                fill={themeColor}
                                opacity="0.2"
                            />
                            <path
                                d={`M 0 ${100 - graphData[0].y} ${graphData.map(p => `L ${p.x} ${100 - p.y}`).join(' ')}`}
                                stroke={themeColor}
                                fill="none"
                                strokeWidth="1.5"
                            />
                        </svg>
                    </div>

                    <IndicatorBar label="Size" value={indicators.size} color={themeColor} />
                    <IndicatorBar label="Velocity" value={indicators.velocity} color={themeColor} />
                    <IndicatorBar label="Stability" value={indicators.stability} color={themeColor} />
                    <IndicatorBar label="Sources" value={indicators.sources} color={themeColor} />

                    {/* ✅ ONLY THIS BLOCK WAS FIXED */}
                    <div className="space-y-4 pt-10 border-t border-white/10 text-[15px] font-bold">
                        <div>
                            <span className="text-white/40 uppercase tracking-widest italic mr-2">
                                Time Horizon:
                            </span>
                            <span className="text-white/90">
                                {selectedData.horizon ?? 'Unknown'}
                            </span>
                        </div>

                        <div>
                            <span className="text-white/40 uppercase tracking-widest italic mr-2">
                                Sources:
                            </span>
                            <span className="italic text-white/90">
                                {sourcesList.length ? sourcesList.join(' • ') : 'N/A'}
                            </span>
                        </div>

                        <div className="pt-4">
                            <span className="text-white/40 uppercase tracking-widest italic mr-2">
                                Recommended Action:
                            </span>
                            <span
                                className="text-2xl font-black uppercase"
                                style={{ color: themeColor }}
                            >
                                {selectedData.action ?? 'WATCH'}
                            </span>
                        </div>
                    </div>
                </motion.div>
            </AnimatePresence>
        </div>
    )
}
