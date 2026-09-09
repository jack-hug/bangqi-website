# -*- coding: utf-8 -*-
"""种子数据 - 首次运行自动建表并插入全部示例数据"""
from extensions import db
from models import (Company, Banner, HomeStat, CompanyImage, EnterpriseCard,
                    DosageForm, Trademark, FuncCategory, Manufacturer,
                    Product, ProductImage,
                    NewsCategory, News, Page, PageSection, PageStat, AdminUser)
from config import Config


def seed_all():
    """建表并插入全部初始数据，仅在数据库为空时执行"""
    db.create_all()

    if Company.query.first():
        print("[seed] 数据库已有数据，跳过种子")
        return

    # ---- 管理员 ----
    admin = AdminUser(username=Config.ADMIN_USERNAME)
    admin.set_password(Config.ADMIN_PASSWORD)
    db.session.add(admin)

    # ---- 公司信息 ----
    company = Company(
        name="邦琪药业",
        full_name="广西邦琪药业有限公司",
        intro="邦琪药业是一家集研发、生产、销售于一体的现代化中成药生产企业，"
              "深耕中药制剂领域三十余载。公司拥有膏剂、糖浆剂、颗粒剂、片剂、胶囊、"
              "搽剂、酊剂、丸剂八大剂型生产线，先后通过国家 GMP 认证，"
              "以传统中医药理论为根基，以现代制药科技为支撑，"
              "致力于为千家万户提供安全、有效、高品质的中成药产品。",
        address="广西壮族自治区钦州市钦州港经济技术开发区邦琪路 1 号",
        phone="0777-8888 888",
        email="contact@bangqipharma.com",
        news_footer=Config.NEWS_FOOTER_DEFAULT,
    )
    db.session.add(company)

    # ---- 首页 Banner ----
    banners = [
        dict(kicker="SINCE 1988 · 匠心中药", title="传承千年岐黄术<br>守护万家灯火明",
             subtitle="集研发、生产、销售于一体的现代化中成药生产企业",
             btn_text="了解邦琪", btn_link="/about", color="ph-green"),
        dict(kicker="八大剂型 · 全线 GMP", title="一盏好膏<br>四十年慢功夫",
             subtitle="煎膏剂年产能达 3000 吨，智能化生产线全程数字管控",
             btn_text="浏览产品", btn_link="/products", color="ph-ta"),
        dict(kicker="道地药材 · 溯源可控", title="好药生于好药材",
             subtitle="广西道地药材规范化种植基地 3 万余亩，来源可查、去向可追",
             btn_text="研发生产", btn_link="/research", color="ph-am"),
        dict(kicker="经典名方 · 二次开发", title="以现代科技<br>唤醒经典名方",
             subtitle="与多所高校共建产学研基地，在研项目 20 余项",
             btn_text="邦琪资讯", btn_link="/news", color="ph-li"),
    ]
    for i, b in enumerate(banners):
        db.session.add(Banner(sort_order=i, is_active=True, **b))

    # ---- 首页统计圆环 ----
    stats = [
        dict(label="生产批文", value="218", unit="个", sort_order=0),
        dict(label="独家品种", value="36", unit="个", sort_order=1),
        dict(label="煎膏剂年产量", value="3000", unit="吨", sort_order=2),
    ]
    for s in stats:
        db.session.add(HomeStat(**s))

    # ---- 公司厂区图片 ----
    ci = [
        dict(title="厂区全景", color="ph-green", sort_order=0),
        dict(title="煎膏车间", color="ph-ta", sort_order=1),
        dict(title="科研大楼", color="ph-am", sort_order=2),
    ]
    for c in ci:
        db.session.add(CompanyImage(**c))

    # ---- 企业相关卡片 ----
    ec = [
        dict(title="组织架构", description="五大中心协同治理，权责清晰",
             link="/about/企业架构", color="ph-green", sort_order=0),
        dict(title="发展历程", description="1988 至今，三十余年深耕中药",
             link="/about/集团介绍", color="ph-am", sort_order=1),
        dict(title="品牌文化", description="传承中药精华，服务大众健康",
             link="/about/社会责任", color="ph-ti", sort_order=2),
        dict(title="科研开发", description="产学研一体，在研项目 20 余项",
             link="/research/产品研发", color="ph-ta", sort_order=3),
    ]
    for e in ec:
        db.session.add(EnterpriseCard(**e))

    # ---- 剂型 ----
    form_data = [
        ("膏剂", "传统煎膏工艺 · 温润滋养"),
        ("糖浆剂", "口感温和 · 老少皆宜"),
        ("颗粒剂", "携带方便 · 冲服即饮"),
        ("片剂", "剂量精准 · 质量稳定"),
        ("胶囊", "掩味良好 · 吸收迅速"),
        ("搽剂", "外用涂抹 · 舒筋活络"),
        ("酊剂", "药材浸提 · 起效迅速"),
        ("丸剂", "药性缓和 · 经典剂型"),
    ]
    form_map = {}
    for i, (name, desc) in enumerate(form_data):
        f = DosageForm(name=name, description=desc, sort_order=i)
        db.session.add(f)
        form_map[name] = f
    db.session.flush()

    # ---- 商标 ----
    tm_data = ["邦琪牌", "琪康牌", "荔春牌"]
    tm_map = {}
    for i, name in enumerate(tm_data):
        t = Trademark(name=name, sort_order=i)
        db.session.add(t)
        tm_map[name] = t
    db.session.flush()

    # ---- 功能分类 ----
    fc_data = ["清热解毒", "止咳化痰", "补益气血", "祛风除湿", "健脾胃", "滋阴补肾"]
    fc_map = {}
    for i, name in enumerate(fc_data):
        fc = FuncCategory(name=name, sort_order=i)
        db.session.add(fc)
        fc_map[name] = fc
    db.session.flush()

    # ---- 生产企业（集团下属企业） ----
    mfg_data = [
        ("邦琪",   "广西邦琪药业集团有限公司主体生产基地",        0),
        ("百琪",   "下属子公司·侧重口服液/糖浆类制剂",           1),
        ("葛洪堂", "下属子公司·侧重经典名方与传统膏方",           2),
    ]
    mfg_map = {}
    for i, (name, desc, so) in enumerate(mfg_data):
        m = Manufacturer(name=name, description=desc, sort_order=so)
        db.session.add(m)
        mfg_map[name] = m
    db.session.flush()

    # ---- 产品 ----
    products_data = [
        dict(name="川贝雪梨膏", form="膏剂", trademark="邦琪牌", func="止咳化痰",
             spec="250g/瓶", indications="养阴润肺，止咳化痰。用于肺热咳嗽、咽干口燥、痰少而粘等症。",
             usage="口服，一次 15g（约一汤匙），一日 2 次，温开水送服。",
             date="2026-03-15", clicks=3215, color="ph-am"),
        dict(name="阿胶补血膏", form="膏剂", trademark="琪康牌", func="补益气血",
             spec="300g/瓶", indications="滋阴补血，补中益气。用于气血两虚所致的头晕乏力、面色萎黄、心悸失眠。",
             usage="口服，一次 20g，一日 2 次，开水冲服。",
             date="2026-03-15", clicks=2874, color="ph-am"),
        dict(name="小儿止咳糖浆", form="糖浆剂", trademark="邦琪牌", func="止咳化痰",
             spec="100ml/瓶", indications="祛痰止咳。用于小儿感冒引起的咳嗽、痰多。",
             usage="口服，2~5 岁一次 5ml，5 岁以上一次 10ml，一日 3 次。",
             date="2026-02-20", clicks=4102, color="ph-gy"),
        dict(name="养阴清肺糖浆", form="糖浆剂", trademark="琪康牌", func="止咳化痰",
             spec="120ml/瓶", indications="养阴润肺，清热利咽。用于咽喉干燥疼痛、干咳少痰、痰中带血。",
             usage="口服，一次 20ml，一日 2 次。",
             date="2026-02-20", clicks=1956, color="ph-gy"),
        dict(name="感冒清热颗粒", form="颗粒剂", trademark="邦琪牌", func="清热解毒",
             spec="12g×10袋/盒", indications="疏风散寒，解表清热。用于风寒感冒、头痛发热、恶寒身痛、鼻流清涕。",
             usage="开水冲服，一次 12g，一日 2 次。",
             date="2026-01-10", clicks=5230, color="ph-gr"),
        dict(name="板蓝根颗粒", form="颗粒剂", trademark="荔春牌", func="清热解毒",
             spec="10g×20袋/盒", indications="清热解毒，凉血利咽。用于感冒发热、咽喉肿痛、温病发热。",
             usage="开水冲服，一次 10g，一日 3~4 次。",
             date="2026-01-10", clicks=4688, color="ph-gr"),
        dict(name="银黄片", form="片剂", trademark="邦琪牌", func="清热解毒",
             spec="0.25g×24片/盒", indications="清热疏风，利咽解毒。用于外感风热所致的咽痛、口渴、发热。",
             usage="口服，一次 2~4 片，一日 3~4 次。",
             date="2025-12-05", clicks=1567, color="ph-ta"),
        dict(name="复方穿心莲片", form="片剂", trademark="琪康牌", func="清热解毒",
             spec="0.35g×36片/盒", indications="清热解毒，凉血消肿。用于感冒发热、咽喉肿痛、口舌生疮。",
             usage="口服，一次 4 片，一日 3 次。",
             date="2025-12-05", clicks=1342, color="ph-ta"),
        dict(name="藿香正气胶囊", form="胶囊", trademark="邦琪牌", func="健脾胃",
             spec="0.3g×12粒/盒", indications="解表化湿，理气和中。用于外感风寒、内伤湿滞所致的头痛昏重、脘腹胀痛、呕吐泄泻。",
             usage="口服，一次 2 粒，一日 2 次。",
             date="2025-11-18", clicks=3890, color="ph-cp"),
        dict(name="消炎利胆胶囊", form="胶囊", trademark="琪康牌", func="清热解毒",
             spec="0.35g×24粒/盒", indications="清热，祛湿，利胆。用于肝胆湿热所致的胁痛、口苦；胆囊炎见上述证候者。",
             usage="口服，一次 2 粒，一日 3 次。",
             date="2025-11-18", clicks=2213, color="ph-cp"),
        dict(name="红花跌打搽剂", form="搽剂", trademark="荔春牌", func="祛风除湿",
             spec="50ml/瓶", indications="活血化瘀，消肿止痛。用于跌打损伤、瘀血肿痛、风湿痹痛。",
             usage="外用，涂搽患处，一日 3~4 次。",
             date="2025-10-22", clicks=1755, color="ph-li"),
        dict(name="风湿骨痛搽剂", form="搽剂", trademark="荔春牌", func="祛风除湿",
             spec="60ml/瓶", indications="祛风除湿，通络止痛。用于风湿性关节炎、骨关节疼痛、肢体麻木。",
             usage="外用，涂搽患处，一日 2~3 次。",
             date="2025-10-22", clicks=1498, color="ph-li"),
        dict(name="祛风活络酊", form="酊剂", trademark="琪康牌", func="祛风除湿",
             spec="30ml/瓶", indications="祛风除湿，舒筋活络。用于风寒湿痹、筋骨疼痛、腰膝酸软。",
             usage="外用，适量涂搽患处，一日 2 次。",
             date="2025-09-30", clicks=921, color="ph-ti"),
        dict(name="复方土槿皮酊", form="酊剂", trademark="邦琪牌", func="清热解毒",
             spec="20ml/瓶", indications="杀菌止痒。用于手足癣、体癣、股癣等皮肤真菌感染。",
             usage="外用，涂搽患处，一日 1~2 次。",
             date="2025-09-30", clicks=868, color="ph-ti"),
        dict(name="六味地黄丸", form="丸剂", trademark="邦琪牌", func="滋阴补肾",
             spec="200粒/瓶", indications="滋阴补肾。用于肾阴亏损所致的头晕耳鸣、腰膝酸软、骨蒸潮热、盗汗遗精。",
             usage="口服，一次 8 丸，一日 3 次。",
             date="2025-09-01", clicks=3054, color="ph-pi"),
        dict(name="补中益气丸", form="丸剂", trademark="琪康牌", func="补益气血",
             spec="200粒/瓶", indications="补中益气，升阳举陷。用于脾胃虚弱、中气下陷所致的体倦乏力、食少腹胀。",
             usage="口服，一次 8 丸，一日 2~3 次。",
             date="2025-09-01", clicks=1136, color="ph-pi"),
    ]
    for idx, pd in enumerate(products_data, start=1):
        p = Product(
            code="BQ-%03d" % idx,
            name=pd["name"], dosage_form_id=form_map[pd["form"]].id,
            trademark_id=tm_map[pd["trademark"]].id,
            func_category_id=fc_map[pd["func"]].id,
            manufacturer_id=mfg_map["邦琪"].id,   # 种子数据全部归到「邦琪」主公司
            spec=pd["spec"], indications=pd["indications"], usage=pd["usage"],
            date=pd["date"], clicks=pd["clicks"], color=pd["color"],
            content=f"{pd['name']}是公司{pd['form']}代表性品种之一，收载于国家药品标准，"
                    f"历经多年临床验证与工艺打磨。本品以道地药材为原料，采用现代化提取工艺"
                    f"与全过程质量控制体系精制而成，具有质量稳定、疗效确切、安全性良好的特点。",
        )
        db.session.add(p)
        db.session.flush()
        # 每个产品 3 张占位图片
        for j, (t, c) in enumerate([
            (pd["name"], pd["color"]), ("包装实拍", "ph-gray"), ("细节展示", "ph-green"),
        ]):
            db.session.add(ProductImage(product_id=p.id, title=t, color=c, sort_order=j))

    # ---- 新闻分类 ----
    nc_data = ["公司新闻", "行业资讯", "家庭护理", "商标展示"]
    nc_map = {}
    for i, name in enumerate(nc_data):
        nc = NewsCategory(name=name, sort_order=i)
        db.session.add(nc)
        nc_map[name] = nc
    db.session.flush()

    # ---- 新闻 ----
    news_data = [
        dict(category="公司新闻", title="邦琪药业煎膏剂生产线技改项目顺利投产，年产能突破 3000 吨",
             date="2026-08-20", clicks=2561,
             content="近日，公司煎膏剂智能化生产线技术改造项目通过自治区药监局验收并正式投产。"
                     "该项目引入全自动浓缩、收膏与灌装设备，实现了从药材前处理到成品出库的全流程"
                     "数字化管控，煎膏剂年产能提升至 3000 吨，产品均一性与稳定性显著提高。"),
        dict(category="行业资讯", title="国家药监局发布中药传承创新发展新政，中成药企业迎来新机遇",
             date="2026-08-12", clicks=1984,
             content="国家药监局近日印发关于促进中药传承创新发展的若干措施，明确提出优化中药"
                     "审评审批机制、鼓励经典名方开发、加强中药材全过程质量控制。业内专家认为，"
                     "具备完整产业链与研发储备的中成药生产企业将率先受益。"),
        dict(category="公司新闻", title="公司与广西中医药大学共建产学研合作基地正式揭牌",
             date="2026-07-28", clicks=1723,
             content="7 月 28 日，邦琪药业与广西中医药大学共建的产学研合作基地在公司研发中心揭牌。"
                     "双方将围绕广西道地药材的综合利用、经典名方的二次开发等课题展开深度合作，"
                     "联合培养中药制药专业人才。"),
        dict(category="家庭护理", title="秋冬换季咳嗽高发，中医教您正确使用止咳类中成药",
             date="2026-07-15", clicks=3098,
             content="秋冬交替之际，昼夜温差加大，咳嗽患者明显增多。中医讲究辨证施治："
                     "风寒咳嗽宜疏风散寒、宣肺止咳；肺热咳嗽宜清热化痰、润肺止咳。"
                     "使用止咳类中成药前应先辨明证型，症状持续一周以上或伴有发热者，请及时就医。"),
        dict(category="家庭护理", title="藿香正气类制剂夏季使用指南：这五个误区要避开",
             date="2026-07-02", clicks=2876,
             content="藿香正气类制剂是夏季家庭药箱的常备药，但使用中存在不少误区："
                     "一并非所有中暑都适用，阳暑不宜；二服用期间应忌生冷油腻；"
                     "三驾驶员及高空作业人员宜选用胶囊剂型；四不宜与头孢类药物同服；"
                     "五症状加重应及时就医。"),
        dict(category="商标展示", title="「邦琪」「琪康」「荔春」三大商标获广西著名商标认定",
             date="2026-06-18", clicks=1215,
             content="公司旗下「邦琪」「琪康」「荔春」三大注册商标凭借良好的市场口碑与品牌影响力，"
                     "荣获广西著名商标认定。三大品牌分别覆盖滋补膏方、常用药与大健康外用线，"
                     "形成了层次分明的品牌矩阵。"),
        dict(category="行业资讯", title="中药材质量追溯体系加快落地，全程可溯源成为行业标配",
             date="2026-06-05", clicks=1092,
             content="随着中药材质量追溯体系在全国范围内加快落地，从种植、采收、加工到投料的"
                     "全链条数据可查询、可追溯正成为行业标配。公司已率先完成主要原料药材的溯源"
                     "系统对接，实现来源可查、去向可追、责任可究。"),
        dict(category="公司新闻", title="公司三款产品进入国家基本药物目录，惠及更多基层患者",
             date="2026-05-22", clicks=1533,
             content="在新版国家基本药物目录中，公司感冒清热颗粒、板蓝根颗粒、六味地黄丸三款"
                     "产品成功入围。基药目录的进入将进一步降低基层患者的用药负担，"
                     "公司承诺持续保障相关产品的稳定供应。"),
    ]
    for nd in news_data:
        db.session.add(News(
            category_id=nc_map[nd["category"]].id,
            title=nd["title"], content=nd["content"],
            date=nd["date"], clicks=nd["clicks"],
        ))

    # ---- 栏目页面 ----
    # section: about / research / contact
    page_defs = {
        "about": [
            dict(title="集团介绍", sort_order=0, stats=[
                ("成立年份", "1988"), ("占地面积", "200+亩"),
                ("员工总数", "1200+"), ("GMP认证", "全线通过"),
            ], sections=[
                ("企业概况", "邦琪药业创建于 1988 年，是一家集中成药研发、生产、销售于一体的现代化制药企业。"
                 "公司占地面积 200 余亩，建筑面积 8 万平方米，现有员工 1200 余人，其中专业技术人员占比超过 35%。"),
                ("发展沿革", "三十余年来，公司始终专注中药制剂领域，从最初的单一半浸膏车间起步，"
                 "逐步建成覆盖八大剂型的现代化生产基地，先后通过多轮国家 GMP 认证与药品上市许可持有人（MAH）制度核查。"),
                ("战略布局", "公司以\"传承中药精华，服务大众健康\"为使命，形成了以广西道地药材资源为依托、"
                 "以经典名方二次开发为引擎、以覆盖全国的 OTC 与基层医疗渠道为支撑的发展格局。"),
            ]),
            dict(title="企业架构", sort_order=1, stats=[], sections=[
                ("治理架构", "公司实行董事会领导下的总经理负责制，下设研发中心、生产中心、质量中心、"
                 "营销中心、职能管理中心五大板块，决策高效、权责清晰。"),
                ("组织体系", "研发中心设中药研究所与分析检测中心；生产中心按剂型划分八个车间；"
                 "质量中心独立行使质量否决权，直属总经理管辖，确保质量管理体系有效运行。"),
                ("人才梯队", "公司建立了管理、技术、技能三通道晋升体系，与多所高校共建人才培养基地，"
                 "持续引进中药学、药物制剂、质量工程等专业人才。"),
            ]),
            dict(title="社会责任", sort_order=2, stats=[], sections=[
                ("药品安全", "公司始终把药品质量安全放在首位，坚持\"质量一票否决\"制度，"
                 "建立覆盖全生命周期的药品追溯体系，连续多年保持产品市场抽检合格率 100%。"),
                ("乡村振兴", "公司在广西多地建立中药材规范化种植基地 3 万余亩，以\"公司+基地+农户\""
                 "模式带动 5000 余户药农增收，助力乡村振兴。"),
                ("公益行动", "历年累计向社会捐赠药品及物资超 3000 万元，在自然灾害、疫情防控等"
                 "公共事件中多次组织紧急驰援。"),
            ]),
            dict(title="企业荣誉", sort_order=3, stats=[], sections=[
                ("资质认证", "国家高新技术企业、自治区级企业技术中心、药品 GMP 认证企业、"
                 "国家知识产权优势企业。"),
                ("品牌荣誉", "「邦琪」商标获评广西著名商标；多个品种入选国家基本药物目录与国家医保目录。"),
                ("科技奖励", "先后承担自治区科技攻关项目 10 余项，获自治区科技进步奖 3 项，"
                 "拥有有效专利 40 余件。"),
            ]),
        ],
        "research": [
            dict(title="产品研发", sort_order=0, stats=[
                ("在研项目", "20+"), ("有效专利", "40+"),
                ("科研人员", "120+"), ("合作高校", "5所"),
            ], sections=[
                ("研发平台", "公司研发中心面积 6000 平方米，设有中药提取分离、制剂工艺、质量分析、"
                 "药理毒理四大功能实验室，配备高效液相色谱仪、气相色谱仪等先进仪器设备百余台套。"),
                ("研发方向", "聚焦经典名方二次开发、中药大品种技术改造与广西道地药材综合利用三大方向，"
                 "在研项目 20 余项，涵盖口服液体制剂、外用制剂等多个领域。"),
                ("产学研合作", "与广西中医药大学、中国药科大学等高校建立长期产学研合作，"
                 "共建联合实验室与实习基地，加速科研成果转化落地。"),
            ]),
            dict(title="质量机构", sort_order=1, stats=[], sections=[
                ("质量体系", "公司建立了覆盖药材源头、生产过程、成品放行到市场反馈的全过程质量管理体系，"
                 "质量受权人对每批产品行使放行决定权。"),
                ("检测能力", "质量中心通过 CMA 认证，可开展性状、鉴别、含量测定、微生物限度等 200 余项检验，"
                 "检测数据全程可追溯。"),
                ("质量文化", "推行\"零缺陷\"质量文化，全员参与质量改进，每年开展 GMP 自检与风险排查，"
                 "持续提升质量管理成熟度。"),
            ]),
            dict(title="生产车间", sort_order=2, stats=[], sections=[
                ("车间概览", "公司建有膏剂、糖浆剂、颗粒剂、片剂、胶囊、搽剂、酊剂、丸剂八个现代化"
                 "生产车间，均按 GMP 标准设计建造，洁净级别满足不同剂型工艺要求。"),
                ("智能制造", "核心车间引入自动化提取、智能化包装与在线监测系统，关键工艺参数实现"
                 "实时采集与自动纠偏，生产数据全程留痕可追溯。"),
                ("产能保障", "煎膏剂年产能达 3000 吨，颗粒剂年产能达 5 亿袋，"
                 "完善的中试车间为新品放大验证提供有力支撑。"),
            ]),
        ],
        "contact": [
            dict(title="联系方式", sort_order=0, stats=[], sections=[
                ("生产地址", "广西壮族自治区钦州市钦州港经济技术开发区邦琪路 1 号"),
                ("联系电话", "0777-8888 888（总机）\n质量投诉专线：0777-8888 666"),
                ("电子邮箱", "contact@bangqipharma.com\n商务合作：bd@bangqipharma.com"),
                ("办公时间", "星期一至星期五 8:30 - 17:30（法定节假日除外）"),
            ]),
            dict(title="商业合作", sort_order=1, stats=[], sections=[
                ("渠道合作", "面向全国招募 OTC 连锁、区域配送商与第三终端合作伙伴，"
                 "提供完善的品类规划、动销支持与培训赋能。"),
                ("原料采购", "常年采购道地中药材与药用辅料，诚邀规范化种植基地、饮片企业洽谈长期战略合作。"),
                ("委托生产", "公司拥有充足的 MAH 受托产能，可承接中药制剂的委托加工与技术转移项目，欢迎来函洽谈。"),
            ]),
            dict(title="企业招聘", sort_order=2, stats=[], sections=[
                ("研发类", "中药学、药物制剂、分析化学等专业硕士及以上学历，负责新药研发与工艺改进。"),
                ("质量类", "药学、微生物学等相关专业本科及以上学历，负责质量检验与 GMP 管理。"),
                ("生产类", "制药工程、机电一体化等专业，负责车间生产与设备管理，接受应届生。"),
                ("简历投递", "hr@bangqipharma.com（邮件标题请注明\"应聘岗位+姓名\"）"),
            ]),
        ],
    }

    for section, pages in page_defs.items():
        for pdef in pages:
            page = Page(section=section, title=pdef["title"], sort_order=pdef["sort_order"])
            db.session.add(page)
            db.session.flush()
            for j, (subtitle, content) in enumerate(pdef["sections"]):
                db.session.add(PageSection(
                    page_id=page.id, subtitle=subtitle, content=content, sort_order=j,
                ))
            for j, (label, value) in enumerate(pdef["stats"]):
                db.session.add(PageStat(
                    page_id=page.id, label=label, value=value, sort_order=j,
                ))

    db.session.commit()
    print("[seed] 种子数据写入完成")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_all()
