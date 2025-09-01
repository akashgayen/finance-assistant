// src/pages/UploadReceipt.tsx
import { useState, useMemo, type SetStateAction } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { createListCollection } from "@chakra-ui/react/collection";
import { Button } from "@chakra-ui/react/button";
import { Card, CardBody } from "@chakra-ui/react/card";
import { Dialog } from "@chakra-ui/react/dialog";
import { Input } from "@chakra-ui/react/input";
import { NativeSelect } from "@chakra-ui/react/native-select";
import { Portal } from "@chakra-ui/react/portal";
import { Select } from "@chakra-ui/react/select";
import { Stack, HStack } from "@chakra-ui/react/stack";
import { Text } from "@chakra-ui/react/text";
import { Textarea } from "@chakra-ui/react/textarea";

type UploadResponse = {
  parsed?: {
    amount?: number | string;
    occurred_at?: string;
    merchant?: string;
    notes?: string;
    currency?: string;
    type?: "income" | "expense";
    category_id?: string;
  };
};

type Category = { id: string; name: string };

const typeOptions = createListCollection({
  items: [
    { label: "Expense", value: "expense" },
    { label: "Income", value: "income" },
  ],
});

export default function UploadReceipt() {
  const qc = useQueryClient();
  const [file, setFile] = useState<File | null>(null);

  // After upload, hold values for editing
  const [isEditOpen, setEditOpen] = useState(false);
  const [typeSel, setTypeSel] = useState<string[]>(["expense"]);
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("INR");
  const [occurredAt, setOccurredAt] = useState(""); // datetime-local
  const [categoryId, setCategoryId] = useState("");
  const [merchant, setMerchant] = useState("");
  const [notes, setNotes] = useState("");

  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get("/categories")).data as Category[],
  });

  // Upload image/PDF and parse
  const upload = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("No file");
      const form = new FormData();
      form.append("file", file);
      return (
        await api.post("/uploads/receipt", form, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data as UploadResponse;
    },
    onSuccess: (data) => {
      const p = data.parsed ?? {};
      // Seed edit form from OCR
      const t =
        p.type === "income" || p.type === "expense" ? p.type : "expense";
      setTypeSel([t]);
      setAmount(p.amount !== undefined ? String(p.amount) : "");
      setCurrency(p.currency ?? "INR");
      // Normalize occurred_at to datetime-local input value if present
      try {
        setOccurredAt(
          p.occurred_at
            ? new Date(p.occurred_at).toISOString().slice(0, 16)
            : ""
        );
      } catch {
        setOccurredAt("");
      }
      setCategoryId(p.category_id ?? "");
      setMerchant(p.merchant ?? "");
      setNotes(p.notes ?? "");
      setEditOpen(true);
    },
  });

  // Save as transaction
  const saveTx = useMutation({
    mutationFn: async () => {
      const type =
        (typeSel as unknown as "income" | "expense" | undefined) ?? "expense";
      const iso = occurredAt
        ? new Date(occurredAt).toISOString()
        : new Date().toISOString();
      return (
        await api.post("/transactions", {
          type: type[0],
          amount: Number(amount),
          currency,
          category_id: categoryId || null,
          merchant: merchant || null,
          notes: notes || null,
          occurred_at: iso,
        })
      ).data;
    },
    onSuccess: async () => {
      setEditOpen(false);
      await qc.invalidateQueries({ queryKey: ["tx"] });
    },
    onError: (err: any) => {
      // Inspect FastAPI's validation errors
      console.error("422 body:", err?.response?.data);
    },
  });

  const canSave = useMemo(() => {
    return (
      amount.trim() !== "" &&
      !Number.isNaN(Number(amount)) &&
      occurredAt.trim() !== ""
    );
  }, [amount, occurredAt]);

  return (
    <Stack gap="4">
      <Input
        type="file"
        accept="image/*,application/pdf"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          setFile(e.currentTarget.files?.[0] ?? null)
        }
      />
      <HStack gap="3">
        <Button
          colorScheme="blue"
          onClick={() => upload.mutate()}
          loading={upload.isPending}
          disabled={!file}
        >
          Upload
        </Button>
        {upload.isError && <Text color="red.500">Upload failed</Text>}
      </HStack>

      {/* Edit & Save dialog */}
      <Dialog.Root
        open={isEditOpen}
        onOpenChange={(e: {
          open: boolean | ((prevState: boolean) => boolean);
        }) => setEditOpen(e.open)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content maxW="lg">
              <Dialog.Header>
                <Dialog.Title>Edit & Save</Dialog.Title>
              </Dialog.Header>
              <Dialog.Body>
                <Stack gap="3">
                  <HStack gap="3" align="start">
                    {/* Type (Select.Root expects string[] when controlled) */}
                    <Select.Root
                      collection={typeOptions}
                      value={typeSel}
                      onValueChange={(e: { value: SetStateAction<string[]> }) =>
                        setTypeSel(e.value)
                      }
                      width="200px"
                    >
                      <Select.HiddenSelect />
                      <Select.Label>Type</Select.Label>
                      <Select.Control>
                        <Select.Trigger>
                          <Select.ValueText placeholder="Choose type" />
                        </Select.Trigger>
                        <Select.IndicatorGroup>
                          <Select.Indicator />
                        </Select.IndicatorGroup>
                      </Select.Control>
                      <Portal>
                        <Select.Positioner>
                          <Select.Content>
                            {typeOptions.items.map((opt) => (
                              <Select.Item item={opt} key={opt.value}>
                                {opt.label}
                                <Select.ItemIndicator />
                              </Select.Item>
                            ))}
                          </Select.Content>
                        </Select.Positioner>
                      </Portal>
                    </Select.Root>

                    <Input
                      type="number"
                      step="0.01"
                      placeholder="Amount"
                      value={amount}
                      onChange={(e: {
                        currentTarget: { value: SetStateAction<string> };
                      }) => setAmount(e.currentTarget.value)}
                    />
                    <Input
                      placeholder="Currency"
                      value={currency}
                      onChange={(e: {
                        currentTarget: { value: SetStateAction<string> };
                      }) => setCurrency(e.currentTarget.value)}
                      width="120px"
                    />
                  </HStack>

                  <HStack gap="3">
                    <Input
                      type="datetime-local"
                      value={occurredAt}
                      onChange={(e: {
                        currentTarget: { value: SetStateAction<string> };
                      }) => setOccurredAt(e.currentTarget.value)}
                    />
                    <NativeSelect.Root width="240px">
                      <NativeSelect.Field
                        value={categoryId}
                        onChange={(e: {
                          currentTarget: { value: SetStateAction<string> };
                        }) => setCategoryId(e.currentTarget.value)}
                      >
                        <option value="">Category (optional)</option>
                        {categories.data?.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.name}
                          </option>
                        ))}
                      </NativeSelect.Field>
                      <NativeSelect.Indicator />
                    </NativeSelect.Root>
                  </HStack>

                  <Input
                    placeholder="Merchant"
                    value={merchant}
                    onChange={(e: {
                      currentTarget: { value: SetStateAction<string> };
                    }) => setMerchant(e.currentTarget.value)}
                  />
                  <Textarea
                    placeholder="Notes"
                    value={notes}
                    onChange={(e: {
                      currentTarget: { value: SetStateAction<string> };
                    }) => setNotes(e.currentTarget.value)}
                  />
                </Stack>
              </Dialog.Body>
              <HStack gap="3" p="4" justify="flex-end">
                <Dialog.CloseTrigger asChild>
                  <Button variant="ghost">Cancel</Button>
                </Dialog.CloseTrigger>
                <Button
                  colorScheme="blue"
                  onClick={() => saveTx.mutate()}
                  loading={saveTx.isPending}
                  disabled={!canSave}
                >
                  Save to Transactions
                </Button>
              </HStack>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>

      {/* Last upload preview (optional compact card) */}
      {upload.data?.parsed && (
        <Card.Root>
          <CardBody>
            <Text>
              Parsed amount: {String(upload.data.parsed.amount ?? "-")}
            </Text>
            <Text>Date: {upload.data.parsed.occurred_at ?? "-"}</Text>
            <Text>Merchant: {upload.data.parsed.merchant ?? "-"}</Text>
          </CardBody>
        </Card.Root>
      )}
    </Stack>
  );
}
