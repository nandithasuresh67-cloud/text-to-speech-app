import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    // In a production app this would report to a logging service.
    console.error('Unexpected UI error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md text-center">
            <h1 className="text-xl font-semibold text-gray-900">Something went wrong</h1>
            <p className="text-gray-500 mt-2">
              Please refresh the page. If the problem continues, try again in a few minutes.
            </p>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
