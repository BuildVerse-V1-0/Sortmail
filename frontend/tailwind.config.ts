import type { Config } from "tailwindcss";

const config: Config = {
	darkMode: ["class"],
	content: [
		"./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/components/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/app/**/*.{js,ts,jsx,tsx,mdx}",
	],
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			colors: {
				// Core palette from spec
				ink: 'var(--ink)',
				paper: 'var(--paper)',
				accent: 'var(--accent)',
				accent2: 'var(--accent2)',
				muted: 'var(--muted)',
				border: 'var(--border)',

				// Surface colors (sidebar, cards, etc.)
				surface: {
					DEFAULT: 'var(--surface)',
					2: 'var(--surface-2)',
					3: 'var(--surface-3)',
					card: 'var(--surface-card)',
					elevated: 'var(--surface-elevated)'
				},

				// Paper variants
				'paper-mid': 'var(--paper-mid)',
				'paper-deep': 'var(--paper-deep)',

				// Ink variants
				'ink-mid': 'var(--ink-mid)',
				'ink-light': 'var(--ink-light)',

				// Semantic/action colors
				success: 'var(--success)',
				warning: 'var(--warning)',
				danger: 'var(--danger)',
				ai: 'var(--ai-purple)',
				'ai-purple': 'var(--ai-purple)',
				'ai-purple-soft': 'var(--ai-purple-soft)',

				// Accent variants
				'accent-hover': 'var(--accent-hover)',
				'accent-soft': 'var(--accent-soft)',

				// Mono/code colors
				'mono-bg': 'var(--mono-bg)',
				'mono-text': 'var(--mono-text)',
				'mono-green': 'var(--mono-green)',
				'mono-blue': 'var(--mono-blue)',
				'mono-orange': 'var(--mono-orange)',
				'mono-yellow': 'var(--mono-yellow)',
				'mono-pink': 'var(--mono-pink)',

				// Wireframe colors
				'wire-bg': 'var(--wire-bg)',
				'wire-border': 'var(--wire-border)',
				'wire-fill': 'var(--wire-fill)',
				'wire-accent': 'var(--wire-accent)',

				// Priority/tag colors
				'tag-urgent': 'var(--tag-urgent)',
				'tag-high': 'var(--tag-high)',
				'tag-medium': 'var(--tag-medium)',
				'tag-low': 'var(--tag-low)',

				// Semantic colors from spec
				'color-ai': 'var(--color-ai)',
				'color-success': 'var(--color-success)',
				'color-warning': 'var(--color-warning)',
				'color-danger': 'var(--color-danger)',

				// Shadcn mappings
				background: 'var(--background)',
				foreground: 'var(--foreground)',
				card: {
					DEFAULT: 'var(--card)',
					foreground: 'var(--card-foreground)'
				},
				popover: {
					DEFAULT: 'var(--popover)',
					foreground: 'var(--popover-foreground)'
				},
				primary: {
					DEFAULT: 'var(--primary)',
					foreground: 'var(--primary-foreground)'
				},
				secondary: {
					DEFAULT: 'var(--secondary)',
					foreground: 'var(--secondary-foreground)'
				},
				destructive: {
					DEFAULT: 'var(--destructive)',
					foreground: 'var(--destructive-foreground)'
				},
				'muted-foreground': 'var(--muted-foreground)',
				input: 'var(--input)',
				ring: 'var(--ring)',
				chart: {
					'1': 'hsl(var(--chart-1))',
					'2': 'hsl(var(--chart-2))',
					'3': 'hsl(var(--chart-3))',
					'4': 'hsl(var(--chart-4))',
					'5': 'hsl(var(--chart-5))'
				}
			},
			fontFamily: {
				display: ['var(--ff-display)'],
				body: ['var(--ff-body)'],
				mono: ['var(--ff-mono)']
			},
			fontSize: {
				xs: '12px',
				sm: '16px',
				base: '18px',
				md: '22px',
				lg: '24px',
				xl: '30px',
				'2xl': '36px'
			},
			spacing: {
				'sb': 'var(--sidebar-w)',
				'sb-col': 'var(--sidebar-collapsed)',
				'tb': 'var(--topbar-h)',
				'panel': 'var(--panel-w)'
			},
			borderRadius: {
				sm: 'var(--radius-sm)',
				md: 'var(--radius-md)',
				lg: 'var(--radius-lg)',
				full: 'var(--radius-full)'
			},
			boxShadow: {
				sm: '0 1px 3px rgba(10, 10, 15, 0.06)',
				md: '0 4px 12px rgba(10, 10, 15, 0.08)',
				lg: '0 8px 32px rgba(10, 10, 15, 0.12)',
				xl: '0 16px 48px rgba(10, 10, 15, 0.16)'
			},
			transitionDuration: {
				instant: '80ms',
				fast: '150ms',
				normal: '250ms',
				slow: '400ms'
			},
			transitionTimingFunction: {
				'ease-out-custom': 'cubic-bezier(0, .6, .4, 1)',
				'ease-spring': 'cubic-bezier(.34, 1.56, .64, 1)'
			},
			animation: {
				'fade-up': 'fadeUp 300ms ease-out',
				'fade-in': 'fadeIn 200ms ease-out',
				'slide-in-right': 'slideInRight 250ms ease-out',
				'shimmer': 'shimmer 1.4s ease-in-out infinite',
				'pulse-dot': 'pulse-dot 2s ease-in-out infinite'
			},
			keyframes: {
				fadeUp: {
					'0%': {
						opacity: '0',
						transform: 'translateY(12px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				fadeIn: {
					'0%': {
						opacity: '0'
					},
					'100%': {
						opacity: '1'
					}
				},
				slideInRight: {
					'0%': {
						opacity: '0',
						transform: 'translateX(16px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},
				shimmer: {
					'0%': {
						backgroundPosition: '-200% 0'
					},
					'100%': {
						backgroundPosition: '200% 0'
					}
				},
				'pulse-dot': {
					'0%, 100%': {
						opacity: '1'
					},
					'50%': {
						opacity: '.4'
					}
				}
			}
		}
	},
	plugins: [require("tailwindcss-animate")],
};

export default config;
