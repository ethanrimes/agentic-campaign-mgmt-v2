// frontend/lib/business-asset-context.tsx

'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface BusinessAsset {
  id: string
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

interface BusinessAssetContextType {
  selectedAsset: BusinessAsset | null
  allAssets: BusinessAsset[]
  setSelectedAsset: (asset: BusinessAsset) => void
  isLoading: boolean
  error: string | null
}

const BusinessAssetContext = createContext<BusinessAssetContextType | undefined>(undefined)

export function BusinessAssetProvider({ children }: { children: ReactNode }) {
  const [selectedAsset, setSelectedAssetState] = useState<BusinessAsset | null>(null)
  const [allAssets, setAllAssets] = useState<BusinessAsset[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load business assets from API
  useEffect(() => {
    const fetchBusinessAssets = async () => {
      try {
        setIsLoading(true)
        const response = await fetch('/api/business-assets')

        if (!response.ok) {
          throw new Error('Failed to fetch business assets')
        }

        const data = await response.json()
        setAllAssets(data.assets || [])

        // Load selected asset from localStorage or use first asset
        const savedAssetId = localStorage.getItem('selectedBusinessAssetId')
        const assetToSelect = savedAssetId
          ? data.assets.find((a: BusinessAsset) => a.id === savedAssetId)
          : data.assets[0]

        if (assetToSelect) {
          setSelectedAssetState(assetToSelect)
        }

        setError(null)
      } catch (err) {
        console.error('Error fetching business assets:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setIsLoading(false)
      }
    }

    fetchBusinessAssets()
  }, [])

  // Persist selected asset to localStorage
  const setSelectedAsset = (asset: BusinessAsset) => {
    setSelectedAssetState(asset)
    localStorage.setItem('selectedBusinessAssetId', asset.id)
  }

  return (
    <BusinessAssetContext.Provider
      value={{
        selectedAsset,
        allAssets,
        setSelectedAsset,
        isLoading,
        error,
      }}
    >
      {children}
    </BusinessAssetContext.Provider>
  )
}

export function useBusinessAsset() {
  const context = useContext(BusinessAssetContext)
  if (context === undefined) {
    throw new Error('useBusinessAsset must be used within a BusinessAssetProvider')
  }
  return context
}
