import { PrismaClient } from '@prisma/client'

const globals = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma =
  globals.prisma ??
  new PrismaClient({
    log: ['query'],
  })

if (process.env.NODE_ENV !== 'production') globals.prisma = prisma
