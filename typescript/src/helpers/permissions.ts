import type { ReplacePermissionError } from '../generated/operations.js'
import { PermissionsResource as GeneratedPermissionsResource } from '../generated/resources.js'
import type { Permission, ReplacePermission } from '../generated/types.js'
import type { Result } from '../runtime/result.js'
import type { WriteOptions } from '../runtime/transport.js'

/** What `permissions.update` changes; a field left out keeps its value */
export interface PermissionChanges {
  readonly licensePlate?: string
  /** `null` for none */
  readonly licensePlateCountry?: string | null
  readonly active?: boolean
  /** `null` removes it */
  readonly supplementalInfo?: string | null
}

/**
 * The fields `update` carries over from the permission. If the API adds a
 * field to `ReplacePermission`, this stops compiling, so that `update`
 * cannot remove the new field by leaving it out.
 */
const CARRIED = [
  'licensePlate',
  'licensePlateCountry',
  'active',
  'supplementalInfo',
] as const satisfies readonly (keyof ReplacePermission)[]
type Uncarried = Exclude<keyof ReplacePermission, (typeof CARRIED)[number]>
const allCarried: [Uncarried] extends [never] ? true : never = true
void allCarried

export class PermissionsResource extends GeneratedPermissionsResource {
  /**
   * Changes some fields of a permission and keeps the others: a `replace`
   * built from the permission as you got it, so that a field you do not
   * mention is not removed. It does not read the permission again.
   *
   * Changing the plate or the country changes the `permissionId`: use the
   * permission this returns from then on.
   */
  update(
    permission: Permission,
    changes: PermissionChanges,
    options: WriteOptions = {}
  ): Promise<Result<Permission, ReplacePermissionError>> {
    return this.replace(
      permission,
      {
        licensePlate: changes.licensePlate ?? permission.licensePlate,
        licensePlateCountry:
          changes.licensePlateCountry !== undefined
            ? changes.licensePlateCountry
            : permission.licensePlateCountry,
        active: changes.active ?? permission.active,
        supplementalInfo:
          changes.supplementalInfo !== undefined
            ? changes.supplementalInfo
            : (permission.supplementalInfo ?? null),
      },
      options
    )
  }
}
