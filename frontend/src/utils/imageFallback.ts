/**
 * 本地图片回退：当 API 的 image_url 为空或为占位图时，使用 frontend/public/images/ 下的静态资源。
 * 与 docs/IMAGE-GENERATION.md 中的命名规则一致。
 */

/** 将人物 en_name 转为文件名 slug，与 IMAGE-GENERATION.md 人物志命名一致 */
export function toFigureSlug(enName: string | null | undefined): string {
  if (!enName || !String(enName).trim()) return ''
  const s = String(enName)
    .toLowerCase()
    .replace(/\./g, '')
    .replace(/[-()]/g, ' ')
    .replace(/\s+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '') // 去掉首尾下划线，避免如 "Shi Qiang (Da Shi)" 产生 shi_qiang_da_shi_
  return s || ''
}

/**
 * 人物志头像 URL：优先用本地 /images/figures/{slug}.webp（与 IMAGE-GENERATION 命名一致），
 * 无 slug 时再用 API 的 image_url，最后用占位图。这样按规则放置的本地图会优先展示。
 */
export function figureImageUrl(
  imageUrl: string | null | undefined,
  enName: string | null | undefined,
  fallbackPlaceholder?: string
): string {
  const slug = toFigureSlug(enName)
  if (slug) return `/images/figures/${slug}.webp`
  if (imageUrl && !imageUrl.includes('placehold.co')) return imageUrl
  return fallbackPlaceholder ?? ''
}

/** 编年史事件标题 → 本地文件名（无扩展名），与 IMAGE-GENERATION.md 编年史表一致 */
const CHRONICLE_TITLE_TO_SLUG: Record<string, string> = {
  '红岸工程立项': 'redcoast1967',
  '第一次红岸发射': 'sunamplifier',
  '不要回答': 'donotanswer',
  '审判日的邀请': 'yereplied',
  '红岸基地撤编与伊文斯接触': 'yeevans',
  '杨冬之死与物理学崩塌': 'yangdong',
  '古筝行动': 'operationguzheng',
  '智子工程与物理学锁死': 'sophonblockade',
  '面壁计划启动': 'wallfacer',
  '罗辑的咒语：187J3X1': 'spell187j3x1',
  '泰勒与雷迪亚兹破壁': 'wallbreaker',
  '阶梯计划：只送大脑': 'staircase',
  '章北海刺杀老航天': 'assassination',
  '末日之战': 'doomsdaybattle',
  '自然选择号逃亡': 'naturalselection',
  '黑暗森林战役': 'darkforestbattle',
  '威慑建立': 'deterrence',
  '希恩斯破壁与钢印族': 'steelstamp',
  '执剑人交接与威慑失败': 'deterrencefail',
  '四维碎片与水滴摧毁': '4dfoil',
  '万有引力号广播': 'gravitybroadcast',
  '程心与云天明会面': 'threetales',
  '三体星系毁灭': 'trisolaris',
  '智子遣返与茶道谈话': 'sophontea',
  '星环城与维德抵抗': 'ringcity',
  '二向箔清理': 'dualvector',
  '冥王星的最后逃亡': 'pluto2d',
  '小宇宙 No.647': 'universe647',
  '回归运动': 'returnmass',
  '三日连珠与 184 号文明毁灭': 'triplesun',
  '双日凌空下的最后一次脱水': 'dehydration'
}

export function toChronicleSlug(title: string | null | undefined): string {
  if (!title || !String(title).trim()) return ''
  const t = String(title).trim()
  return CHRONICLE_TITLE_TO_SLUG[t] ?? t.replace(/\s+/g, '_').toLowerCase().replace(/[^\w\u4e00-\u9fff_-]/g, '')
}

/**
 * 编年史视觉记录图 URL：优先用 API 的 image_url（且非 picsum/placehold），否则用本地 /images/chronicles/{slug}.webp
 */
export function chronicleImageUrl(
  imageUrl: string | null | undefined,
  title: string | null | undefined
): string {
  if (imageUrl && !imageUrl.includes('picsum.photos') && !imageUrl.includes('placehold.co')) return imageUrl
  const slug = toChronicleSlug(title)
  if (slug) return `/images/chronicles/${slug}.webp`
  return ''
}
