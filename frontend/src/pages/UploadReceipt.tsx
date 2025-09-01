import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '../lib/api'
import { Stack, Button, Input, Text, Card, CardBody } from '@chakra-ui/react'

export default function UploadReceipt() {
  const [file, setFile] = useState<File | null>(null)
  const mut = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file')
      const form = new FormData()
      form.append('file', file)
      return (await api.post('/uploads/receipt', form, { headers: { 'Content-Type': 'multipart/form-data' } })).data
    }
  })
  return (
    <Stack gap="4">
      <Input type="file" accept="image/*,application/pdf" onChange={(e)=>setFile(e.target.files?.[0] || null)} />
      <Button colorScheme="blue" onClick={()=>mut.mutate()} loading={mut.isPending} disabled={!file}>Upload</Button>
      {mut.isError && <Text color="red.500">Upload failed</Text>}
      {mut.data && (
        <Card.Root><CardBody>
          <Text>Amount: {mut.data.parsed?.amount ?? '-'}</Text>
          <Text>Date: {mut.data.parsed?.occurred_at ?? '-'}</Text>
          <Text>Merchant: {mut.data.parsed?.merchant ?? '-'}</Text>
        </CardBody></Card.Root>
      )}
    </Stack>
  )
}
