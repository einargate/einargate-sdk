import type { Event, Gate, Permission } from '../src/index.js'

export const gate: Gate = {
  gateId: 'g1',
  locationId: 'mock-location',
  name: 'Main gate',
  manualOperation: true,
  gateControlCameraId: 'c1',
  createdAt: new Date('2026-09-12T10:41:07.000Z'),
  updatedAt: new Date('2026-09-12T10:41:07.000Z'),
}

export const permission: Permission = {
  permissionId: 'ABC123|HU',
  locationId: 'mock-location',
  gateId: 'g1',
  cameraId: 'c1',
  licensePlate: 'ABC123',
  licensePlateCountry: 'HU',
  ownerUserId: 'u1',
  active: true,
  supplementalInfo: 'Visitor',
  numberOfOpenings: 3,
  createdAt: new Date('2026-09-12T10:41:07.000Z'),
  updatedAt: new Date('2026-09-12T10:41:07.000Z'),
}

export function event(eventId: string, eventTime: string): Event {
  return {
    eventId,
    type: 'AutomaticGateOpening',
    status: 'finalized',
    locationId: 'mock-location',
    gateId: 'g1',
    cameraId: 'c1',
    eventTime: new Date(eventTime),
    createdAt: new Date(eventTime),
    updatedAt: new Date(eventTime),
  }
}
