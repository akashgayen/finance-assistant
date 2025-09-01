import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import {
  Stack,
  Button,
  Input,
  Text,
  HStack,
  Table,
} from "@chakra-ui/react";

export default function UploadPdf() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [preview, setPreview] = useState<any[]>([]);

  const upload = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("No file");
      const form = new FormData();
      form.append("file", file);
      return (
        await api.post("/imports/history-pdf", form, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data;
    },
    onSuccess: (data) => {
      setJobId(data.job_id);
      setPreview(data.preview || []);
    },
  });

  const commit = useMutation({
    mutationFn: async () => {
      if (!jobId) throw new Error("No job");
      return (await api.post(`/imports/${jobId}/commit`)).data;
    },
  });

  return (
    <Stack gap="4">
      <Input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <Button
        colorScheme="blue"
        onClick={() => upload.mutate()}
        loading={upload.isPending}
        disabled={!file}
      >
        Upload PDF
      </Button>
      {upload.isError && <Text color="red.500">Upload failed</Text>}

      {preview.length > 0 && (
        <>
          <Table.Root size="sm">
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>Date</Table.ColumnHeader>
                <Table.ColumnHeader>Type</Table.ColumnHeader>
                <Table.ColumnHeader>Amount</Table.ColumnHeader>
                <Table.ColumnHeader>Merchant</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {preview.map((r: any, i: number) => (
                <Table.Row key={i}>
                  <Table.Cell>{r.occurred_at}</Table.Cell>
                  <Table.Cell>{r.type}</Table.Cell>
                  <Table.Cell>{r.amount}</Table.Cell>
                  <Table.Cell>{r.merchant}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table.Root>
          <HStack>
            <Button
              colorScheme="green"
              onClick={() => commit.mutate()}
              loading={commit.isPending}
              disabled={!jobId}
            >
              Commit Import
            </Button>
            {commit.isSuccess && (
              <Text color="green.600">
                Imported {commit.data?.inserted || 0} rows
              </Text>
            )}
            {commit.isError && <Text color="red.500">Commit failed</Text>}
          </HStack>
        </>
      )}
    </Stack>
  );
}
