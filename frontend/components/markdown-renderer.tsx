"use client"

import React from "react"
import ReactMarkdown from "react-markdown"

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-sm dark:prose-invert max-w-none ${className}`}>
      <ReactMarkdown
        components={{
          // Customize heading styles
          h1: ({ children }) => (
            <h1 className="mb-2 text-lg font-bold text-foreground/90">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="mb-2 text-base font-bold text-foreground/90">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-2 text-sm font-semibold text-foreground/85">{children}</h3>
          ),
          // Customize list styles
          ul: ({ children }) => (
            <ul className="mb-2 ml-4 list-inside list-disc space-y-1 text-foreground/80">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-2 ml-4 list-inside list-decimal space-y-1 text-foreground/80">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-sm leading-relaxed">
              {children}
            </li>
          ),
          // Customize emphasis
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground/95">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-foreground/85">{children}</em>
          ),
          // Customize code
          code: ({ children }) => (
            <code className="rounded bg-muted/50 px-1.5 py-0.5 font-mono text-xs text-foreground/80">
              {children}
            </code>
          ),
          // Customize code blocks
          pre: ({ children }) => (
            <pre className="mb-2 overflow-x-auto rounded-lg bg-muted/50 p-3 text-xs">
              {children}
            </pre>
          ),
          // Customize paragraphs
          p: ({ children }) => (
            <p className="mb-2 text-sm leading-relaxed text-foreground/85">{children}</p>
          ),
          // Customize blockquotes
          blockquote: ({ children }) => (
            <blockquote className="mb-2 border-l-4 border-primary/40 pl-3 italic text-foreground/70">
              {children}
            </blockquote>
          ),
          // Customize links
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline hover:text-primary/80"
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
