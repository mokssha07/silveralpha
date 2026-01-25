'use client'

import { motion, Variants } from 'framer-motion'

interface TypingTextProps {
    text: string
    className?: string
    delay?: number
    stagger?: number
    once?: boolean
}

export default function TypingText({
    text,
    className = "",
    delay = 0,
    stagger = 0.02,
    once = true
}: TypingTextProps) {
    // Split text into lines, then characters, preserving spaces and line breaks
    const lines = text.split('\n')

    const container: Variants = {
        hidden: { opacity: 0 },
        visible: (i: number = 1) => ({
            opacity: 1,
            transition: {
                staggerChildren: stagger,
                delayChildren: delay,
            },
        }),
    }

    const child: Variants = {
        visible: {
            opacity: 1,
            y: 0,
            transition: {
                type: "spring",
                damping: 12,
                stiffness: 100,
            },
        },
        hidden: {
            opacity: 0,
            y: 20,
            transition: {
                type: "spring",
                damping: 12,
                stiffness: 100,
            },
        },
    }

    const alignmentClass = className.includes('justify-end') ? 'justify-end' : className.includes('justify-center') ? 'justify-center' : ''

    return (
        <motion.div
            variants={container}
            initial="hidden"
            whileInView="visible"
            viewport={{ once }}
            className={`flex flex-wrap ${className}`}
        >
            {lines.map((line, lineIndex) => (
                <div key={lineIndex} className={`w-full flex flex-wrap ${alignmentClass}`}>
                    {line.split(" ").map((word, wordIndex, wordArray) => (
                        <div key={wordIndex} className={`flex whitespace-nowrap ${wordIndex < wordArray.length - 1 ? 'mr-[0.25em]' : ''}`}>
                            {word.split("").map((char, charIndex) => (
                                <motion.span
                                    variants={child}
                                    key={charIndex}
                                    className="inline-block"
                                >
                                    {char}
                                </motion.span>
                            ))}
                        </div>
                    ))}
                </div>
            ))}
        </motion.div>
    )
}
