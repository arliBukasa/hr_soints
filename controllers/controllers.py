# -*- coding: utf-8 -*-
import logging
from array import array

from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request, Response
import json

class HrSoints(http.Controller):
    comparateur={"eq":"=","contains":"like"}
    @http.route('/hr_soints/dependants/', auth='public', type="json", methods=["GET"], website=False,csrf=False)
    def index(self, **kw):
        listEnfants=[]

        for enfant in request.env["hr.employee.family"].sudo().search([],order="employee_id asc"):
            id=enfant.employee_id.id if enfant.employee_id else False
            employeeName = enfant.employee_id.name if enfant.employee_id else False
            listEnfants.append({"id":enfant.id, "employee":id,"employeeName":employeeName,"relation":enfant.relation})
        logging.info(f"========================= enfants:{listEnfants}")
        return  Response({'dependants': listEnfants }, content_type='application/json')

    @http.route('/hr_soints/dependantes/delete', type='http', auth='public', cors='*')
    def deleteItems(self,ids=[], **kwargs):
        # Votre logique pour récupérer les données
        res={"status":"echec"}
        if len(ids) >0:
            delecting=request.env["hr.employee.family"].sudo().search([("id","in",ids)], order="employee_id asc")
            logging.info(f"*************************** delecting items: {delecting}")
            res["status"] = "success"
        response = request.make_response(json.dumps(res))
        response.headers[
            'Access-Control-Allow-Origin'] = '*'  # Autorise toutes les origines (à adapter selon vos besoins)
        response.headers['Content-Type'] = 'application/json'

        return response

    @http.route('/hr_soints/dependantes', type='http', auth='public', cors='*')
    def get_dependants(self,**kwargs):
        limit=30
        order = "id asc"
        if "pageSize" in kwargs:
            limit=int(kwargs["pageSize"])
            logging.info(f"*********************************************** limit: {limit}")
        if "sorters[0][field]" in kwargs:
            order =kwargs["sorters[0][field]"]+" "+kwargs["sorters[0][order]"]
        logging.info(f"*********************************************** order {order}")
        # Votre logique pour récupérer les données
        listEnfants = request.env["hr.employee.family"].sudo().search([], order=order,limit=limit)
        listEmployees=[]
        for employee in request.env["hr.employee"].sudo().search([], order=order,limit=limit):
            logging.info(f"*********************************************** fams_ids: {employee.fam_ids}")
            enfants=[]
            #if employee.fam_ids:
            for Enfant in employee.fam_ids:
                #enfants.append({"id": Enfant.id,"name":Enfant.member_name,"relation": Enfant.relation})
                enfants.append([[Enfant.id],[Enfant.member_name,Enfant.relation]])
            listEmployees.append({"id":employee.id,"name":employee.name,"genre":employee.gender,"position":employee.job_id.name,"company":employee.department_id.name,"familly":enfants})

        # Créez la réponse JSON avec l'en-tête CORS approprié

        response = request.make_response(json.dumps(listEmployees))
        response.headers['Access-Control-Allow-Origin'] = '*'  # Autorise toutes les origines (à adapter selon vos besoins)
        response.headers['Content-Type'] = 'application/json'

        return  response

    @http.route('/hr_soints/listdependants', type='json', methods=["POST"], auth='public', cors='*',csrf=False)
    def get_listdependants(self, **kwargs):
        order = "id asc"
        logging.info(f"*********************************************** enfants: { kwargs } {request.params}")
        res=[]
        if "rids" in kwargs:
            ids=kwargs["rids"]
            logging.info(f"*********************************************** enfants: {ids}")
            listEnfants = request.env["hr.employee.family"].sudo().search([("id","in",ids)], order=order)
            for Enfant in listEnfants:
                res.append({"id": Enfant.id,"name":Enfant.member_name,"relation": Enfant.relation})
            logging.info(f"*********************************************** enfants: {res}")

        # Créez la réponse JSON avec l'en-tête CORS approprié

        """response = request._json_response(result=json.dumps(res))
        response.headers[
            'Access-Control-Allow-Origin'] = '*'  # Autorise toutes les origines (à adapter selon vos besoins)
        response.headers['Content-Type'] = 'application/json'
        """
        return res

    @http.route('/hr_soints/familly', type='http', auth='public', cors='*')
    def get_familly(self, **kwargs):
        # Votre logique pour récupérer les données
        listEmployees = []
        enfants=[]
        if "ids" in kwargs:

            listEmployees = request.env["hr.employee.family"].sudo().search([("id","in",kwargs["ids"])], order="employee_id asc")

        for enfant in listEmployees:

            enfants.append({"id": enfant.id, "name": enfant.member_name, "relation": enfant.relation})

        # Créez la réponse JSON avec l'en-tête CORS approprié

        response = request.make_response(json.dumps(enfants))
        response.headers[
            'Access-Control-Allow-Origin'] = '*'  # Autorise toutes les origines (à adapter selon vos besoins)
        response.headers['Content-Type'] = 'application/json'

        return response

    @http.route('/employees', type='http', auth='public', cors='*')
    def employees(self,**kwargs):
        # Votre logique pour récupérer les données
        {'_end': '10', '_order': 'desc', '_sort': 'id', '_start': '0', 'name_like': 'ANT'}
        limit = 20
        order = "id asc"
        domain=[]
        offset=0
        if "_end" in kwargs and "_start" in kwargs:
            limit = int(kwargs.get("_end"))- int(kwargs.get("_start"))
            offset=int(kwargs.get("_end"))
            logging.info(f"*********************************************** limit: {limit}")
        if "_sort" in kwargs:
            order = kwargs.get("_sort")+ " " + kwargs.get("_order")
            logging.info(f"*********************************************** order {order}")
        if "name_like" in kwargs and kwargs.get("name_like") not in [False,None]:
            domain.append(("name","ilike",kwargs.get("name_like")))
        if "genre_like" in kwargs and kwargs.get("genre_like") not in [False,None]:
            domain.append(("gender","ilike",kwargs.get("genre_like")))
        logging.info(f"******************************************** {limit,order,domain,kwargs}")
        # Votre logique pour récupérer les données
        listEnfants = request.env["hr.employee.family"].sudo().search([])
        listEmployees = []
        for employee in request.env["hr.employee"].sudo().search(domain, order=order, limit=limit,offset=offset):
            enfants = []
            for Enfant in listEnfants:
                if (employee.id == Enfant.employee_id.id):
                    enfants.append({"id": Enfant.id, "name": Enfant.member_name, "relation": Enfant.relation})
            listEmployees.append(
                {"id": employee.id, "name": employee.name, "genre": employee.gender, "position": employee.job_id.name,
                 "company": employee.department_id.name, "familly": enfants})

        response = request.make_response(json.dumps(listEmployees))
        response.headers[
            'Access-Control-Allow-Origin'] = '*'  # Autorise toutes les origines (à adapter selon vos besoins)
        response.headers['Content-Type'] = 'application/json'

        return response

    @http.route(['/categories','/posts'], type='http', auth='public', cors='*')
    def postes(self, **kwargs):
        # Votre logique pour récupérer les données
        logging.info(f"=================== ")
        listEnfants = request.env["hr.employee.family"].sudo().search([], order="employee_id asc")
        listEmployees = [
    {
        "id": 1004,
        "title": "tyutyur",
        "content": "ryurtyur",
        "category": {
            "id": 1
        }
    },
    {
        "id": 1003,
        "title": "efwe",
        "status": "published",
        "category": {
            "id": "7"
        },
        "content": "sfsadf"
    },
    {
        "id": 1002,
        "title": "efssfsef",
        "status": "rejected",
        "category": {
            "id": 3
        },
        "content": "efsfseefsefs ef s fefs fs eefs"
    },
    {
        "id": 1002,
        "title": "tesasdfasdf",
        "status": "published",
        "category": {
            "id": 3
        },
        "content": "tesasdfsadfsadfsadfsdfsa"
    },
    {
        "id": 1001,
        "title": "dfgf",
        "content": "hfghg",
        "status": "published",
        "category": {
            "id": 7,
            "title": "Books & Magazines"
        }
    },
    {
        "id": 1001,
        "title": "asdszdXCFGVHB",
        "category": {
            "id": 1
        }
    },
    {
        "id": 1001,
        "title": "asdf",
        "status": "published",
        "category": {
            "id": "4"
        },
        "content": "sadfsadf"
    },
    {
        "id": 1000,
        "title": "Accusantium quasi ad et laudantium eligendi qui sunt harum.",
        "slug": "illo-architecto-asperiores",
        "content": "Quasi eveniet sit et nam ipsam fuga nam eveniet. Ut qui ipsam error sunt dolore cum odio. Quibusdam qui magnam ducimus asperiores rerum consequuntur dolor a. Esse esse laborum et illo sed est accusantium dolores autem. Et corporis aut tempora at et. Eligendi hic quidem est. Ea voluptatem ex unde nisi illo aut officia. Omnis unde itaque voluptate omnis facere. Dolor corporis excepturi similique quidem non. Rerum ullam iste corporis beatae odit dignissimos fugit.",
        "hit": 294052,
        "category": {
            "id": 14
        },
        "user": {
            "id": 27
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-01-09T06:55:59.624Z",
        "publishedAt": "2024-01-02T12:10:15.616Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "d1a4a896-d48b-4376-90e9-c46671d24100",
                "status": "done",
                "type": "image/jpeg",
                "uid": "f3fb894d-92fa-46b9-9a54-1544c611d4c8"
            }
        ],
        "tags": [
            8
        ],
        "language": 3
    },
    {
        "id": 999,
        "title": "Laudantium rerum ut sequi labore cum molestiae alias aut necessitatibus.",
        "slug": "recusandae-nihil-et",
        "content": "Consequatur qui eveniet. Nostrum consequuntur perspiciatis vero quasi rerum beatae. Qui voluptates similique facilis autem deleniti ad. Quasi nemo fugiat qui dicta est quia hic. Eius occaecati minima quaerat et. Quasi voluptates ratione sapiente. Quod repellat minima autem libero molestiae sed. Itaque consequatur aut dicta asperiores repudiandae dolores. Quis consectetur voluptatem adipisci voluptatem occaecati velit assumenda iure. Et eius repellat voluptatem libero doloribus quas cumque.",
        "hit": 912077,
        "category": {
            "id": 1
        },
        "user": {
            "id": 40
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2022-03-26T11:07:47.190Z",
        "publishedAt": "2023-03-15T17:45:37.962Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "9164d6e8-f79c-48d5-8fa8-acd7bbb2917d",
                "status": "done",
                "type": "image/jpeg",
                "uid": "1c128492-9cd7-4fe6-9334-6c86cb34da26"
            }
        ],
        "tags": [
            5,
            3
        ],
        "language": 2
    },
    {
        "id": 998,
        "title": "Cumque consequatur vitae atque dolores quis illum est nulla ullam.",
        "slug": "qui-delectus-qui",
        "content": "Itaque dolor nam. In ipsa ut doloribus. Nihil ipsam fugiat ad maxime aut aut. Omnis voluptas et rerum repudiandae occaecati alias optio maiores. Magnam libero ut et qui numquam perferendis dolore doloribus. Impedit provident beatae nihil itaque a illum nihil qui dolor. Reiciendis enim tenetur fugit necessitatibus. Quod nesciunt ipsam et omnis est. Sint dolores repudiandae sunt sed eius velit a odio enim. Accusantium iusto nemo molestiae nulla aspernatur.",
        "hit": 847503,
        "category": {
            "id": 1
        },
        "user": {
            "id": 48
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-04-16T11:14:33.796Z",
        "publishedAt": "2024-01-26T05:46:22.288Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "243c14d9-65e1-4e9e-8408-9d0914d68851",
                "status": "done",
                "type": "image/jpeg",
                "uid": "5d70d5ef-ed52-4522-bb9d-f7f5deeaf1bb"
            }
        ],
        "tags": [
            9,
            10,
            4
        ],
        "language": 2
    },
    {
        "id": 997,
        "title": "Consectetur ut facere.",
        "slug": "sed-id-dolores",
        "content": "Voluptatem qui eius culpa. Quas et non aut. A voluptate et quaerat vel vitae ex. Quae numquam velit praesentium. In id ut sit neque et hic sequi et harum. Est dolore tenetur quia perspiciatis sequi. Quia et odit sunt unde. Earum debitis cupiditate labore. Possimus quia ut est consequuntur est. Eius explicabo voluptatibus exercitationem illum.",
        "hit": 773510,
        "category": {
            "id": 13
        },
        "user": {
            "id": 40
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2024-01-22T19:25:51.357Z",
        "publishedAt": "2022-07-15T18:30:03.699Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "7ea8aba8-1835-4127-a645-ed19158b9edb",
                "status": "done",
                "type": "image/jpeg",
                "uid": "f74dad61-e716-4d55-b2e0-73031acb9c40"
            }
        ],
        "tags": [
            6,
            3
        ],
        "language": 3
    },
    {
        "id": 996,
        "title": "Deleniti quo harum eius praesentium nulla debitis recusandae.",
        "slug": "accusantium-atque-aut",
        "content": "Expedita ipsa et repellat esse natus repudiandae ut consequatur. Provident tempore quisquam numquam alias aut et consequatur asperiores et. Aut aut molestiae nihil quisquam maiores et est reiciendis. Dolore blanditiis itaque rerum et rem nulla. Voluptas corporis omnis iure non rerum molestiae possimus maiores. Nam quia quis saepe deserunt eos labore quae corporis. Dolores rerum omnis reprehenderit esse voluptatibus consequatur dolor sed vitae. Recusandae beatae deleniti. Libero voluptates aut pariatur distinctio. Quo est vel ex vel.",
        "hit": 23071,
        "category": {
            "id": 11
        },
        "user": {
            "id": 13
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2023-08-12T04:51:05.960Z",
        "publishedAt": "2023-04-30T21:10:40.795Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "ede1784e-67db-464f-812d-1aa0d812556c",
                "status": "done",
                "type": "image/jpeg",
                "uid": "df234721-c51c-4647-8cbe-2e53adf4d47d"
            }
        ],
        "tags": [
            2,
            9,
            8
        ],
        "language": 2
    },
    {
        "id": 995,
        "title": "At aut velit.",
        "slug": "ratione-distinctio-rem",
        "content": "Et hic non delectus atque est reprehenderit aut veritatis. Aut reiciendis consequatur maxime vel. Vitae hic nam optio voluptatem doloremque repellendus ipsam ex libero. Velit architecto et aspernatur. Delectus dolores deserunt mollitia facilis esse neque et. Ab qui quia veniam corporis odio. Nam vel quaerat. Magnam architecto est. Possimus et libero voluptas ullam magnam eligendi sed. Veniam animi est cum voluptate rerum ad expedita nobis corrupti.",
        "hit": 314322,
        "category": {
            "id": 6
        },
        "user": {
            "id": 9
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-07-18T08:15:21.162Z",
        "publishedAt": "2023-10-30T16:03:15.722Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "ff9aa3ef-ba6a-4168-aaa0-ff43853d6f31",
                "status": "done",
                "type": "image/jpeg",
                "uid": "fafa0bd4-afa5-498b-94b6-c6a7353f65ea"
            }
        ],
        "tags": [
            5,
            7
        ],
        "language": 1
    },
    {
        "id": 994,
        "title": "Et tenetur exercitationem molestiae maiores.",
        "slug": "sit-vero-ut",
        "content": "Facere dicta quae. Enim architecto id maiores tempora reprehenderit. Nesciunt delectus harum voluptate qui veniam quia qui. Voluptatem assumenda quibusdam. Soluta voluptatem consequatur voluptatum et dolorem. Qui nihil dolores. Est ut est qui excepturi ab dolores nam unde. Fugit provident qui expedita aliquam. Quia dolore consequatur eaque accusantium est qui eligendi quis. Rem aut saepe.",
        "hit": 747359,
        "category": {
            "id": 9
        },
        "user": {
            "id": 8
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-11-25T21:22:55.639Z",
        "publishedAt": "2022-11-28T03:04:30.952Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "43e9080a-f063-4854-b32e-22f26d0d594b",
                "status": "done",
                "type": "image/jpeg",
                "uid": "92ee730e-25a0-423d-89da-07b2a741c0d8"
            }
        ],
        "tags": [
            6,
            5
        ],
        "language": 2
    },
    {
        "id": 993,
        "title": "Eum saepe officia sed voluptate praesentium.",
        "slug": "ipsa-officiis-a",
        "content": "Sint commodi sed error aut atque. Non praesentium praesentium deleniti eius veniam. Illum harum doloremque sit est vel iusto laboriosam. Laborum totam voluptatem et iste aut voluptate ducimus quia nisi. Optio excepturi expedita qui cumque culpa in illum qui quam. Iusto cupiditate et placeat dicta et recusandae natus. Unde aspernatur natus et odio nulla dicta qui officia ipsa. Fugit sed soluta corporis omnis neque officiis. Dolorem velit quam autem voluptatum placeat repudiandae. Vitae repellat repudiandae expedita quo eveniet amet.",
        "hit": 456328,
        "category": {
            "id": 2
        },
        "user": {
            "id": 41
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2023-01-06T12:21:19.768Z",
        "publishedAt": "2023-09-02T04:32:21.336Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "3448f03c-20c4-49d7-8d4c-07fc95599f5f",
                "status": "done",
                "type": "image/jpeg",
                "uid": "d4b4551e-b122-4744-ad0d-4fe5b38e1b35"
            }
        ],
        "tags": [
            4,
            10,
            1
        ],
        "language": 3
    },
    {
        "id": 992,
        "title": "Rerum dicta magni.",
        "slug": "est-quis-quis",
        "content": "Perferendis doloribus nesciunt. Non perferendis modi ratione ipsa vero. Voluptas qui et rerum qui aut vero. Aspernatur qui dolorem incidunt non. Quasi facilis inventore sequi ipsa mollitia cupiditate debitis atque architecto. Quidem quos possimus at sint quibusdam eos numquam saepe. Quasi unde quo. Tempore rerum rerum sit totam earum laboriosam soluta illum. Enim nostrum omnis est debitis consequuntur quas. Commodi qui voluptatem provident optio vel ipsum nostrum dolore.",
        "hit": 70731,
        "category": {
            "id": 2
        },
        "user": {
            "id": 10
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2024-01-26T01:18:53.977Z",
        "publishedAt": "2023-08-30T14:00:49.433Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "809f2d8c-ca1e-4a9f-9e81-23efcfb97fe7",
                "status": "done",
                "type": "image/jpeg",
                "uid": "7fc8dee0-79c7-47e6-941b-73aad6a17227"
            }
        ],
        "tags": [
            6,
            5
        ],
        "language": 1
    },
    {
        "id": 991,
        "title": "Dolores nihil saepe cumque iusto fugiat ullam est.",
        "slug": "dolor-earum-delectus",
        "content": "Rerum nemo temporibus omnis. In ab quia esse modi sed voluptatem minus aut. Nemo fugit amet perspiciatis consequatur excepturi eum. Libero voluptatem minus fugit voluptate qui asperiores et recusandae inventore. Et sequi quia possimus. Dolor provident non illum ut sint. Voluptatem necessitatibus sunt earum ea fugit unde. Excepturi praesentium modi at. Doloremque culpa libero eum et similique. Sed rerum sequi cumque qui et vel.",
        "hit": 687491,
        "category": {
            "id": 13
        },
        "user": {
            "id": 21
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-11-15T08:24:09.437Z",
        "publishedAt": "2023-07-06T09:29:22.790Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "0589cea9-6546-4917-81d9-8d9870200f36",
                "status": "done",
                "type": "image/jpeg",
                "uid": "c59d7f4a-e4e3-4212-ac3f-2b97d4d34b74"
            }
        ],
        "tags": [
            6
        ],
        "language": 2
    },
    {
        "id": 990,
        "title": "Fuga mollitia molestiae non sapiente omnis explicabo quia nulla illum.",
        "slug": "quae-non-omnis",
        "content": "Minima ut commodi eaque aperiam earum quam sint sed. Voluptas autem pariatur eum et blanditiis. Iure voluptatem magnam. Molestias laborum inventore laborum fugit praesentium vel. Ducimus corporis et. Sed ab sunt et molestias rem accusamus. Quis vel totam suscipit cupiditate ea et et. Vel quae sit qui odit quia aliquam reiciendis tenetur. Omnis tempore earum corrupti amet nam odit voluptatem totam ut. Ducimus reiciendis cupiditate iste in sed iure ab.",
        "hit": 528699,
        "category": {
            "id": 12
        },
        "user": {
            "id": 29
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-11-11T15:06:19.158Z",
        "publishedAt": "2022-05-23T06:53:08.799Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "fd0bb222-6cb4-41a9-8f4f-0e9f2f27f844",
                "status": "done",
                "type": "image/jpeg",
                "uid": "d0424a5d-45e8-4584-a91c-6f4a46b5f73f"
            }
        ],
        "tags": [
            2,
            1
        ],
        "language": 2
    },
    {
        "id": 989,
        "title": "Praesentium ullam vitae.",
        "slug": "facere-ullam-eos",
        "content": "Quisquam dolores eveniet pariatur nam numquam aspernatur. Ut rerum officiis ducimus maxime sint aperiam. Aut amet quis et aut nihil voluptatem. Quo doloribus error aut dolor eum. Est voluptates omnis placeat fuga ab nesciunt sequi nostrum. Recusandae consequatur expedita ut. Quidem odio voluptas officia eos. Et non voluptatem. Architecto repellat excepturi ex quaerat tempore fugit in et. Pariatur libero qui suscipit.",
        "hit": 126762,
        "category": {
            "id": 10
        },
        "user": {
            "id": 6
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2022-05-01T11:13:08.680Z",
        "publishedAt": "2023-03-28T18:55:09.495Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "3703f80f-1ed9-4a11-920c-15c355b20332",
                "status": "done",
                "type": "image/jpeg",
                "uid": "aed7a0d0-e014-4b87-b57b-2337020ce09b"
            }
        ],
        "tags": [
            10,
            7
        ],
        "language": 2
    },
    {
        "id": 988,
        "title": "Distinctio quo qui enim nisi.",
        "slug": "consequatur-qui-odit",
        "content": "Aliquam et itaque architecto unde quis voluptas qui. Deleniti voluptatem nobis reiciendis vitae et quis tempore reiciendis. Molestiae et voluptatibus et quis autem laudantium iusto distinctio sit. Sunt nostrum error aut. Optio ratione saepe in libero iste laboriosam voluptas. Fugiat dolores beatae nostrum. Itaque aperiam aut qui est architecto sed sint sit. Maxime et qui quo ut consequatur provident illum aperiam. Delectus vitae culpa nobis vitae temporibus et. Consequatur aspernatur quasi reprehenderit reprehenderit quis voluptate recusandae qui.",
        "hit": 133556,
        "category": {
            "id": 15
        },
        "user": {
            "id": 12
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-11-22T16:12:12.395Z",
        "publishedAt": "2023-07-20T12:24:59.725Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "98befc16-80c3-48c8-b0dd-5d8ef2376f04",
                "status": "done",
                "type": "image/jpeg",
                "uid": "7112ef20-5260-4877-b5b2-b3dec2cd5f12"
            }
        ],
        "tags": [
            5
        ],
        "language": 3
    },
    {
        "id": 987,
        "title": "Sit nihil quo qui.",
        "slug": "non-sunt-doloribus",
        "content": "Qui repudiandae numquam quia. Debitis sunt ipsam. Et repudiandae aspernatur quis sed magnam earum qui unde amet. Repellendus perspiciatis molestiae. Eius illum ducimus odit numquam. Nemo et eligendi odit nihil qui quia atque. Eius accusamus dolor cupiditate et vitae voluptatem commodi ut sit. Blanditiis quis sed temporibus eum facilis repellendus rerum. Et maiores id voluptates quisquam rerum sed unde quos id. Optio ullam esse id autem eum quae rerum natus sapiente.",
        "hit": 371774,
        "category": {
            "id": 7
        },
        "user": {
            "id": 14
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2022-12-23T05:52:08.531Z",
        "publishedAt": "2023-03-04T23:19:07.142Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "e3fb2e2b-d91e-461d-9e90-061691005030",
                "status": "done",
                "type": "image/jpeg",
                "uid": "886cc548-5ca0-411f-abdf-8fe81f893c6d"
            }
        ],
        "tags": [
            3,
            1,
            10
        ],
        "language": 1
    },
    {
        "id": 986,
        "title": "Aut nisi incidunt officia voluptatem eligendi.",
        "slug": "sunt-commodi-est",
        "content": "Ipsam ut facilis quia rerum enim unde. Iure illum quia quaerat occaecati et aut deleniti quas vel. Ut laboriosam eum. Vel facilis repudiandae omnis repellat a. Vero debitis aliquid quas recusandae. Necessitatibus eum ut. Error beatae sunt quia in ipsa est vitae illum. Dolor eos vitae. Mollitia voluptatem voluptatem ut veritatis incidunt molestiae quisquam itaque. Repellendus quos nisi hic explicabo qui velit et deleniti recusandae.",
        "hit": 882518,
        "category": {
            "id": 1
        },
        "user": {
            "id": 14
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-02-05T16:40:09.092Z",
        "publishedAt": "2023-12-06T18:29:30.497Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "f42120fb-867a-41d6-9931-0b4c651ed2f8",
                "status": "done",
                "type": "image/jpeg",
                "uid": "8ab9e27e-227f-4c08-946e-37532fb8465a"
            }
        ],
        "tags": [
            7,
            5,
            8
        ],
        "language": 3
    },
    {
        "id": 985,
        "title": "Eos dolor ad.",
        "slug": "et-voluptatibus-qui",
        "content": "Aut qui omnis vel sint magni. Accusamus amet est nisi similique voluptates. Quibusdam et omnis est aliquid repellat vel. Et ex et tempore non repellendus odio dolorem et. Iusto dolores aliquam animi omnis saepe et et. Pariatur aliquid et quis. Laboriosam tempore praesentium. Maiores qui et voluptatem aut earum nostrum sequi itaque. Ea debitis ducimus velit amet hic a ducimus. Temporibus accusantium sunt quo natus nobis quaerat.",
        "hit": 711634,
        "category": {
            "id": 15
        },
        "user": {
            "id": 31
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-05-29T19:03:49.567Z",
        "publishedAt": "2022-07-09T03:42:52.253Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "1d5fe31e-90af-4fc7-9fc8-e01f15cb0578",
                "status": "done",
                "type": "image/jpeg",
                "uid": "4ae271b8-b484-45f7-9d00-31fe8969a6d5"
            }
        ],
        "tags": [
            8
        ],
        "language": 1
    },
    {
        "id": 984,
        "title": "Natus ut libero ut tenetur et et ullam et velit.",
        "slug": "facilis-quia-in",
        "content": "Est quisquam non repudiandae. Soluta esse quia quos quod vitae deserunt libero. Corporis ut ratione est quo adipisci est eum culpa incidunt. Id consequatur ut nisi quibusdam quibusdam consequatur. Doloremque quia non est dolores vitae consequatur sunt. Quo ut dolores. Et dolores doloremque dolor vero voluptatum quia ea praesentium. Voluptas nihil vitae ipsam hic odit sed. Ut quaerat ullam molestiae voluptas. Omnis voluptatem voluptatem perspiciatis.",
        "hit": 276491,
        "category": {
            "id": 15
        },
        "user": {
            "id": 36
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2022-12-22T01:57:33.997Z",
        "publishedAt": "2023-01-24T13:53:28.633Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "6e2f088d-6cfa-4fa2-be45-bc2edf22dcad",
                "status": "done",
                "type": "image/jpeg",
                "uid": "2fcfb9e6-21fd-4520-b323-4edd3e089e1f"
            }
        ],
        "tags": [
            8,
            6,
            9
        ],
        "language": 2
    },
    {
        "id": 983,
        "title": "Unde doloribus qui aut eius maiores fugit ea consequatur ut.",
        "slug": "consequatur-rerum-quo",
        "content": "Quasi itaque quaerat est reprehenderit corrupti voluptates quae. Vel et expedita rerum. Magnam itaque iure quidem incidunt aut et eaque nesciunt. Quia hic aliquid unde. Vel dolores eligendi sit tenetur atque sed ea. Voluptates labore nesciunt. Ut et eos qui eaque magnam quod ipsum ea eum. Et molestiae iure consequatur non nihil eum praesentium est voluptatem. Corporis veritatis ut alias quam corporis et. Error iusto sit voluptatem consequuntur veniam nihil ipsam libero.",
        "hit": 975333,
        "category": {
            "id": 4
        },
        "user": {
            "id": 11
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2023-10-11T18:51:03.628Z",
        "publishedAt": "2023-06-20T22:50:48.704Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "a635c2fc-c1a8-4392-8982-bc2764e9c7f8",
                "status": "done",
                "type": "image/jpeg",
                "uid": "ea074dbf-a0e9-4826-ac07-c289ca5cedb9"
            }
        ],
        "tags": [
            1,
            2,
            8
        ],
        "language": 2
    },
    {
        "id": 982,
        "title": "Culpa animi consequatur ex deleniti nesciunt id quod.",
        "slug": "porro-alias-reiciendis",
        "content": "Tempore natus quia rerum. Eum quidem ex voluptatem. Corporis dolorem sed consectetur tenetur ut quis voluptatum. Nostrum a facilis omnis maxime harum ut. Quod consectetur voluptas. Doloremque maxime doloribus quos. Aliquid quod exercitationem ullam. Veritatis odit sequi voluptatem iste qui et. Quas sit reiciendis iure cum facilis quibusdam ipsum blanditiis. Et nihil iusto qui saepe porro.",
        "hit": 441957,
        "category": {
            "id": 9
        },
        "user": {
            "id": 16
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2022-03-28T04:33:47.009Z",
        "publishedAt": "2022-11-12T08:36:00.956Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "b6a8a67d-855a-4f73-8fb1-15994a57f261",
                "status": "done",
                "type": "image/jpeg",
                "uid": "ccf23df0-4383-456f-bfed-ed9a2579a561"
            }
        ],
        "tags": [
            8
        ],
        "language": 3
    },
    {
        "id": 981,
        "title": "Aut ut ipsa.",
        "slug": "aut-sint-sequi",
        "content": "Nemo sed dolor consequuntur alias adipisci quia sit enim debitis. Et consequatur praesentium qui cum quia. Animi facilis sit ut molestias. Deserunt impedit qui dolorem fugit expedita asperiores vitae enim. Vero totam incidunt. Laborum aspernatur dignissimos laborum nesciunt dolore aspernatur voluptas vitae magnam. Non accusantium accusantium nam omnis aspernatur. Eos porro debitis id quod. Illo nihil et. Unde quas ut necessitatibus soluta veritatis distinctio.",
        "hit": 7893,
        "category": {
            "id": 1
        },
        "user": {
            "id": 27
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-06-09T02:41:14.283Z",
        "publishedAt": "2022-06-15T00:36:30.133Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "0cd5387d-62eb-4d24-8355-356d98f61fe8",
                "status": "done",
                "type": "image/jpeg",
                "uid": "31479a0a-ce05-4043-9235-923e66df7c58"
            }
        ],
        "tags": [
            3,
            5,
            1
        ],
        "language": 3
    },
    {
        "id": 980,
        "title": "Molestiae praesentium dolor et ut.",
        "slug": "molestias-ducimus-ex",
        "content": "Aut sint et ipsum placeat et aut ut. Omnis molestias possimus. Accusamus vero fugit quod corporis non quidem quia. Reprehenderit voluptatem dolore tempore doloremque nam. Expedita sint nulla iusto ad placeat quam. Dolores quis consequatur iste. Qui provident ipsa odit. Officiis quas aliquid suscipit. Amet numquam sit assumenda maiores error doloribus. Omnis vel iste commodi quos ea molestias aspernatur officiis non.",
        "hit": 409496,
        "category": {
            "id": 6
        },
        "user": {
            "id": 6
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-05-09T03:11:13.898Z",
        "publishedAt": "2023-01-05T09:53:55.403Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "21c984ed-1ed4-434d-9a4a-8f8cff5ff0f9",
                "status": "done",
                "type": "image/jpeg",
                "uid": "2badbaf1-411a-4877-9d0a-d4f945fc3a7d"
            }
        ],
        "tags": [
            6,
            8
        ],
        "language": 1
    },
    {
        "id": 979,
        "title": "Molestias modi quia commodi sed quisquam numquam dolore provident.",
        "slug": "possimus-perferendis-incidunt",
        "content": "Autem beatae quia voluptatem non exercitationem. Neque voluptatem esse voluptates. Ex minus quia et officiis. Ratione impedit at et illo. Et quod aut repudiandae veritatis. Veniam quasi error odit dolor maxime dolor qui iusto. Ipsam officia provident hic. Unde iste quae commodi tempore. Culpa veniam deleniti provident laboriosam amet. Est repellendus blanditiis enim tenetur perspiciatis.",
        "hit": 740560,
        "category": {
            "id": 13
        },
        "user": {
            "id": 48
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2023-11-10T15:44:36.566Z",
        "publishedAt": "2023-08-12T20:35:54.255Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "7318ffef-c9d8-4493-a276-8b044e1492fe",
                "status": "done",
                "type": "image/jpeg",
                "uid": "6b3eb1c5-cf2e-4aeb-a384-a72c7868c43e"
            }
        ],
        "tags": [
            4,
            5
        ],
        "language": 1
    },
    {
        "id": 978,
        "title": "Rem consequatur repellendus.",
        "slug": "nemo-quis-soluta",
        "content": "Debitis doloremque consequatur maiores voluptatibus qui repudiandae. Reiciendis dolorum mollitia nesciunt. Est ea dolores et corrupti est. Ut ex consequatur. Minus molestias asperiores quo deleniti odio similique voluptatem. Voluptas itaque tempora enim dolores omnis quaerat error aperiam enim. Accusantium ex temporibus quibusdam repudiandae nesciunt eum. Cumque praesentium occaecati molestiae minima voluptatibus sint nesciunt deserunt rerum. Quia est ratione sit nam ducimus eveniet illo et. Ipsam quae ratione sit magni magnam.",
        "hit": 288908,
        "category": {
            "id": 10
        },
        "user": {
            "id": 37
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-10-19T00:07:06.673Z",
        "publishedAt": "2022-06-24T01:41:10.487Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "99252478-2615-498a-9c9e-42814a1c864b",
                "status": "done",
                "type": "image/jpeg",
                "uid": "a6148ef5-10fc-49eb-b8a3-9c6daff8b0bc"
            }
        ],
        "tags": [
            3,
            8
        ],
        "language": 1
    },
    {
        "id": 977,
        "title": "Facilis veniam ut quaerat nisi facere quo quibusdam adipisci praesentium.",
        "slug": "quibusdam-aut-fugiat",
        "content": "Dolor necessitatibus quod quisquam. Quaerat eum dolor est fugiat harum dignissimos. Dignissimos qui laborum aut est. Maiores corrupti beatae sed est. Rerum facilis possimus aut et sequi. Qui assumenda alias. Temporibus aspernatur sit id maxime. Quos et perspiciatis accusamus rerum rerum. Iste perspiciatis non fugit. Harum dolor nisi qui eum quasi aut.",
        "hit": 229237,
        "category": {
            "id": 13
        },
        "user": {
            "id": 7
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-11-08T04:53:00.996Z",
        "publishedAt": "2023-04-14T00:45:09.517Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "07a9a689-67aa-422a-9ec0-f6f3c6926721",
                "status": "done",
                "type": "image/jpeg",
                "uid": "19daba9a-5ba7-49a8-bfc7-f7d58170d01c"
            }
        ],
        "tags": [
            8,
            7
        ],
        "language": 3
    },
    {
        "id": 976,
        "title": "Consequuntur ut optio eius ullam ut dolor dolorem dolorum.",
        "slug": "quas-ut-illo",
        "content": "Deserunt aperiam soluta deserunt nobis similique doloremque exercitationem eum aut. Possimus quis cum. Animi ea eaque voluptatibus voluptatem et dolore aperiam. Sed modi quasi qui eum eaque saepe quia incidunt sequi. Quasi officiis perspiciatis rerum exercitationem. Voluptatibus optio quas labore qui. Qui magnam sit esse esse officiis laboriosam et ipsam et. Qui eius maxime ipsum ipsa distinctio. Incidunt iste inventore veritatis et ut. Commodi tempora perspiciatis et veritatis fuga aperiam qui veritatis.",
        "hit": 302161,
        "category": {
            "id": 1
        },
        "user": {
            "id": 13
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-02-26T07:20:53.890Z",
        "publishedAt": "2023-06-12T13:09:05.458Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "b4acdef6-bb33-4cf8-adc6-fa953297619e",
                "status": "done",
                "type": "image/jpeg",
                "uid": "7f3e8efd-82a2-45cb-a7ff-4368327bf782"
            }
        ],
        "tags": [
            8,
            3,
            2
        ],
        "language": 3
    },
    {
        "id": 975,
        "title": "Quia et neque aut sit velit impedit voluptatem sequi.",
        "slug": "voluptatem-sed-quo",
        "content": "Quia consequatur harum fuga possimus mollitia. Non laboriosam saepe pariatur nihil quia molestiae doloribus repellat. Et perferendis consequatur numquam. Unde libero recusandae quaerat fugit accusamus earum placeat dicta voluptas. Et dolor itaque perspiciatis. Nostrum autem ipsa est rem harum corrupti delectus illum laudantium. Sequi officia sint. Ea voluptate consequatur. Repellendus libero officia dolorem non saepe qui sed. Atque alias unde a harum enim.",
        "hit": 291416,
        "category": {
            "id": 7
        },
        "user": {
            "id": 42
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-05-20T15:12:53.789Z",
        "publishedAt": "2022-06-21T23:54:09.589Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "efb267f2-f212-46cc-b47c-926dedd509a4",
                "status": "done",
                "type": "image/jpeg",
                "uid": "121364fd-6df0-4f7f-b9e1-f14570ad8fc6"
            }
        ],
        "tags": [
            2,
            9
        ],
        "language": 3
    },
    {
        "id": 974,
        "title": "Ratione non optio nisi.",
        "slug": "non-earum-possimus",
        "content": "Repellendus quos sequi labore neque quo autem. Porro modi provident unde illum laudantium. Accusamus velit ea ut doloribus saepe sint. Cupiditate alias aut deserunt odit ipsa qui occaecati. Aspernatur beatae quia. Iste doloribus omnis minus quod aut sed incidunt. Nulla aliquid sunt nobis ut. Veniam magnam quaerat pariatur sed. Voluptatibus at est odio animi molestiae. Eveniet odit tenetur doloremque.",
        "hit": 382962,
        "category": {
            "id": 8
        },
        "user": {
            "id": 43
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-04-19T21:09:27.358Z",
        "publishedAt": "2024-02-04T02:02:56.611Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "a0044d72-3dd6-4609-b937-be577959af76",
                "status": "done",
                "type": "image/jpeg",
                "uid": "155efafd-af6e-45be-884f-6a32c8332bee"
            }
        ],
        "tags": [
            2,
            8
        ],
        "language": 1
    },
    {
        "id": 973,
        "title": "Aliquid vel beatae eligendi.",
        "slug": "minus-tempore-molestias",
        "content": "Nisi tempora et alias provident. Voluptas reiciendis voluptates. Dolor voluptatum reiciendis quisquam consequatur ea tempora neque dolores mollitia. Voluptatem esse sunt natus ratione. In quas sit reprehenderit. Voluptatem sit cupiditate sit velit sint optio expedita dicta. Quisquam voluptatum architecto aut voluptas qui tempora tempore sit eius. Accusantium perferendis doloremque placeat. Doloribus laudantium et temporibus id. Vel accusamus ducimus autem.",
        "hit": 379844,
        "category": {
            "id": 2
        },
        "user": {
            "id": 44
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-04-25T20:46:22.574Z",
        "publishedAt": "2022-11-08T16:17:28.757Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "60208eb6-dc1c-4673-98f7-8d087d6d73e6",
                "status": "done",
                "type": "image/jpeg",
                "uid": "da2d2c60-3cbf-4683-9105-17a8414729f7"
            }
        ],
        "tags": [
            3
        ],
        "language": 3
    },
    {
        "id": 972,
        "title": "Quis fugiat non occaecati voluptates.",
        "slug": "non-fuga-ab",
        "content": "Et repellat repellendus quod aut eveniet quisquam molestias. Impedit molestias dignissimos esse illum et ullam sed officiis fugiat. Sunt natus ut. Laborum itaque placeat quasi. In cumque molestias provident voluptatum itaque quos totam necessitatibus. Ut optio voluptatem sapiente eum id atque. Ut commodi id enim vitae magnam. Minus quos reiciendis. Commodi sed et natus non dolorem. Ut dicta maiores pariatur consequatur sapiente enim corrupti suscipit.",
        "hit": 815527,
        "category": {
            "id": 6
        },
        "user": {
            "id": 22
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-11-17T10:53:44.043Z",
        "publishedAt": "2022-07-11T22:01:16.857Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "f5f61ea8-e0ca-4b7a-9b11-2ed7c1ecc50c",
                "status": "done",
                "type": "image/jpeg",
                "uid": "a1d213aa-5aea-4e0f-ba34-cd8c0e6a2acc"
            }
        ],
        "tags": [
            10
        ],
        "language": 2
    },
    {
        "id": 971,
        "title": "Suscipit dolor adipisci dignissimos dolor dolore esse et.",
        "slug": "laborum-numquam-voluptatum",
        "content": "Consectetur aut delectus rem dolorum voluptas et beatae. Quia quia dolorem beatae voluptas laborum sunt ut. Sequi ut assumenda labore. Et et itaque aut esse doloremque. Est sunt ratione labore ut. Sunt consequatur enim. Qui quibusdam at veniam aut sequi eaque perferendis. Aut beatae quae fugiat reiciendis repellendus deserunt. Ipsum nisi fugit in soluta et sed voluptates. Quam suscipit impedit animi labore sunt est.",
        "hit": 489355,
        "category": {
            "id": 1
        },
        "user": {
            "id": 33
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2022-06-16T13:46:13.558Z",
        "publishedAt": "2022-06-11T12:59:24.045Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "61d5e648-ce1d-4830-8f40-3b453f2b8631",
                "status": "done",
                "type": "image/jpeg",
                "uid": "8c943f18-482f-46f1-be24-4577d94ab724"
            }
        ],
        "tags": [
            4
        ],
        "language": 3
    },
    {
        "id": 970,
        "title": "Sint tempora et maxime consectetur eaque libero nulla sint autem.",
        "slug": "fugiat-voluptas-velit",
        "content": "Rerum aspernatur impedit. Necessitatibus excepturi qui qui aliquam sunt expedita libero ab. Unde debitis iste officia reiciendis molestiae consequatur quod et. Est dolor consequatur eligendi. Est quam voluptatum consequatur. Odio consequatur quaerat. Numquam pariatur qui doloremque nihil ipsa. Debitis iusto quo molestiae. Aut eveniet eos. Nostrum suscipit quas.",
        "hit": 435161,
        "category": {
            "id": 14
        },
        "user": {
            "id": 38
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-08-10T07:59:32.672Z",
        "publishedAt": "2023-04-12T12:06:28.661Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "9b6278c3-776d-4b1c-8d9c-2450b85755a3",
                "status": "done",
                "type": "image/jpeg",
                "uid": "41a895b4-d0f2-45aa-8e92-7ffe516f14db"
            }
        ],
        "tags": [
            4,
            7
        ],
        "language": 3
    },
    {
        "id": 969,
        "title": "Molestiae at officiis quas quasi.",
        "slug": "vel-et-rem",
        "content": "Enim tempore ullam praesentium eum iusto et neque. Iusto ut aspernatur et dignissimos quis omnis accusantium. Nihil nulla temporibus voluptatem. Est esse magnam quasi odio maxime nisi nihil natus. Tempore ipsum ipsam eos autem. Tenetur nihil tempora architecto ut laboriosam molestiae. Molestias distinctio maxime nihil nihil voluptatibus consequatur magni. Praesentium laboriosam sint error. Eius impedit consequuntur earum cum. Consequatur libero libero et adipisci nobis expedita.",
        "hit": 775269,
        "category": {
            "id": 1
        },
        "user": {
            "id": 49
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-04-08T03:39:17.192Z",
        "publishedAt": "2023-10-03T06:04:49.642Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "35770323-ab68-4380-919a-6fe348d60c37",
                "status": "done",
                "type": "image/jpeg",
                "uid": "99d29684-61cc-455f-a007-dcdb4cefa9a1"
            }
        ],
        "tags": [
            2,
            4,
            10
        ],
        "language": 3
    },
    {
        "id": 968,
        "title": "Blanditiis rerum quo minima sit veniam.",
        "slug": "culpa-vero-earum",
        "content": "Distinctio consectetur quasi quia consequatur aut enim culpa. Saepe rerum ipsam sed ut omnis totam deserunt. Dolorum eos qui. Quibusdam suscipit cumque eligendi sit. Aut nulla laborum maxime culpa vel ex eum quibusdam laudantium. Distinctio quas qui nobis non officia vero. Aliquid velit est sapiente ad maxime ipsum nobis nihil soluta. Magnam ipsam quis. Voluptatibus optio qui. Enim perferendis dolores doloremque corporis aut quia.",
        "hit": 215098,
        "category": {
            "id": 8
        },
        "user": {
            "id": 41
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-06-25T07:28:01.381Z",
        "publishedAt": "2022-11-22T20:05:17.450Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "1d84091d-325c-4e45-bc25-4edf5233dfaa",
                "status": "done",
                "type": "image/jpeg",
                "uid": "a6d1e881-4e99-4a44-ba32-6052b2bc8247"
            }
        ],
        "tags": [
            6,
            5
        ],
        "language": 3
    },
    {
        "id": 967,
        "title": "Rem atque libero earum expedita corporis voluptates eum.",
        "slug": "autem-voluptate-et",
        "content": "Non aspernatur ut ut non dolores. Voluptatem facere modi. Quibusdam veritatis quia. Quasi eos praesentium tenetur voluptatum praesentium nam qui sunt totam. Sed sit omnis soluta quo id autem eius. Dolore suscipit eius. Praesentium harum ipsum optio nulla autem aut laboriosam et. Aliquam at laboriosam sunt et voluptas. Id porro officiis tempora est repellendus itaque eum quo. Minima explicabo et velit asperiores eaque consequatur neque eaque veniam.",
        "hit": 207102,
        "category": {
            "id": 8
        },
        "user": {
            "id": 17
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2023-04-23T19:26:07.844Z",
        "publishedAt": "2024-01-06T13:24:13.836Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "59114d10-9c70-4c99-9834-3c5ac767f666",
                "status": "done",
                "type": "image/jpeg",
                "uid": "d6be32ba-2732-4b48-9b7f-93cfb5e303b4"
            }
        ],
        "tags": [
            5,
            1,
            7
        ],
        "language": 2
    },
    {
        "id": 966,
        "title": "Et nihil adipisci vel laboriosam incidunt eos consequuntur.",
        "slug": "sint-dolor-et",
        "content": "Eaque et reiciendis et harum quae qui ut dolorum facere. Sit vero ipsam vel similique dolore laborum labore et aperiam. Deleniti voluptatibus dolorem. Ipsa veniam suscipit atque nemo fugiat voluptatem possimus quo. Totam eaque voluptatibus. Nostrum ad modi delectus enim voluptas ratione quia voluptatem aliquam. Quasi at et aperiam est necessitatibus porro iusto id culpa. Autem sint nobis deleniti sunt earum accusamus officiis cupiditate. Qui porro ut dolorum voluptatum impedit aut. Voluptatem possimus sint.",
        "hit": 363765,
        "category": {
            "id": 4
        },
        "user": {
            "id": 22
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-01-22T11:12:14.326Z",
        "publishedAt": "2023-04-26T22:23:10.544Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "41a41291-6d29-4833-87b9-2c6fe2f06624",
                "status": "done",
                "type": "image/jpeg",
                "uid": "ddd1996a-3dac-4e0b-b80a-908c3bfec969"
            }
        ],
        "tags": [
            1,
            6,
            9
        ],
        "language": 1
    },
    {
        "id": 965,
        "title": "Tenetur dolore quae eos excepturi consectetur quia in et.",
        "slug": "velit-perspiciatis-incidunt",
        "content": "Quia eos nulla quisquam quia architecto sed. Sed reprehenderit aspernatur. Adipisci ratione et vel et labore sed sit explicabo animi. Aut ipsa sit provident. Dicta fugiat quis harum non ipsa velit nihil molestiae corrupti. Qui reiciendis a et commodi culpa incidunt suscipit in repudiandae. Aut quo perspiciatis illum nulla architecto sit labore sint error. Molestiae eveniet non ut quam corrupti laudantium ipsa. Est a et ut soluta nobis totam. Voluptatem accusantium perspiciatis ducimus distinctio ut sint eius voluptatum officiis.",
        "hit": 191577,
        "category": {
            "id": 14
        },
        "user": {
            "id": 43
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2024-01-23T22:21:36.913Z",
        "publishedAt": "2023-09-01T19:47:09.046Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "53297762-a43a-4e75-b0f9-10beab0f1628",
                "status": "done",
                "type": "image/jpeg",
                "uid": "78d57069-b3fb-49aa-bfdb-6f4a50317f8f"
            }
        ],
        "tags": [
            8,
            3,
            5
        ],
        "language": 3
    },
    {
        "id": 964,
        "title": "Perferendis laborum optio recusandae quia ratione accusantium velit.",
        "slug": "eligendi-omnis-error",
        "content": "Culpa corporis aliquid vel aut quod. Et totam sit. Neque vero aspernatur odit tenetur qui ut corporis. Labore suscipit rerum ducimus sit voluptatem explicabo. Maxime praesentium quo quo ipsam libero earum nobis. Debitis et omnis. Nostrum quaerat sit ut. Libero corporis recusandae perferendis sit ad omnis. Dolorem dolores et est et. Voluptas quo a vel.",
        "hit": 973159,
        "category": {
            "id": 13
        },
        "user": {
            "id": 49
        },
        "status": "rejected",
        "status_color": "red",
        "createdAt": "2022-05-16T07:24:15.368Z",
        "publishedAt": "2023-12-30T21:19:02.030Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "e0fb67ef-a738-4850-9d2b-b0f2b8e8291b",
                "status": "done",
                "type": "image/jpeg",
                "uid": "87ce2fc0-8b8e-4765-9b25-c9bf534b95a7"
            }
        ],
        "tags": [
            6,
            5
        ],
        "language": 1
    },
    {
        "id": 963,
        "title": "Aliquam ut repudiandae quis expedita voluptas aut sit.",
        "slug": "culpa-rerum-quam",
        "content": "Quasi et modi perspiciatis omnis provident totam omnis est. Accusamus modi quis cumque tenetur. Consequuntur aliquam rerum in quia explicabo et tempore ipsam. Voluptatem qui corporis est. Sed est amet repudiandae incidunt corrupti. Aut impedit eos. Deserunt et ducimus qui voluptatem. Non voluptates dolore tempora molestias animi. Dolores non quae est. Sit neque temporibus enim nihil.",
        "hit": 287457,
        "category": {
            "id": 12
        },
        "user": {
            "id": 17
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-03-11T16:00:06.302Z",
        "publishedAt": "2023-05-13T21:30:43.308Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "040bf359-7f9a-4883-b8d3-5fb916ba50bc",
                "status": "done",
                "type": "image/jpeg",
                "uid": "2d2940db-58a4-4f8b-ad2e-c263bb5062b4"
            }
        ],
        "tags": [
            3,
            8
        ],
        "language": 2
    },
    {
        "id": 962,
        "title": "Ea quia et aliquam et incidunt.",
        "slug": "ut-ea-aperiam",
        "content": "Nam quibusdam inventore sint praesentium molestiae sequi nesciunt. Rerum ipsum ut officia est voluptatem nulla est maxime. Adipisci consequuntur sequi dolorem blanditiis ad fuga eos autem. Et ut nemo et aliquid dignissimos atque incidunt. Sed porro placeat tenetur totam. Reiciendis aut ipsum ea maxime id et asperiores cum. Ad ut ipsam aspernatur sint et corrupti. Velit quia enim sapiente in voluptatibus id rerum consequatur. Quam rerum animi et libero error ut perferendis delectus. Dolorem autem omnis consequuntur voluptas.",
        "hit": 447990,
        "category": {
            "id": 12
        },
        "user": {
            "id": 8
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-12-15T20:44:23.341Z",
        "publishedAt": "2022-03-23T01:38:53.961Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "0b23a95e-855b-4ddd-9f8a-2dd7cf6928f4",
                "status": "done",
                "type": "image/jpeg",
                "uid": "3c1eec7f-5b7c-4b70-9c38-0ddb4f1a028f"
            }
        ],
        "tags": [
            3
        ],
        "language": 3
    },
    {
        "id": 961,
        "title": "Temporibus quo quia.",
        "slug": "aut-at-ut",
        "content": "Adipisci optio voluptatum omnis. Voluptatem inventore dolor non perspiciatis tempora magnam aperiam fugiat. Et possimus quasi non commodi fuga et. Omnis dicta incidunt aperiam laudantium voluptate consequatur. Natus voluptas aut in id quisquam quia. Sit non eos esse laboriosam odit eos tempore nam velit. Corporis vel et ad quia soluta ea dignissimos rerum. Tempore sit expedita nulla dolorem nihil est. Unde quia qui recusandae consectetur maxime eum ut facere distinctio. Dolorem voluptas repellendus nesciunt sit veritatis voluptas aut corrupti.",
        "hit": 985587,
        "category": {
            "id": 9
        },
        "user": {
            "id": 17
        },
        "status": "draft",
        "status_color": "orange",
        "createdAt": "2022-09-04T01:16:12.731Z",
        "publishedAt": "2022-05-19T03:37:48.707Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "9ed136cb-183c-4973-aa35-6f17bdc4228d",
                "status": "done",
                "type": "image/jpeg",
                "uid": "b1774eb2-681d-455a-ac0e-f2a3569a56b9"
            }
        ],
        "tags": [
            3,
            6,
            8
        ],
        "language": 3
    },
    {
        "id": 960,
        "title": "Voluptatum beatae possimus reprehenderit.",
        "slug": "omnis-saepe-voluptas",
        "content": "Non sunt ipsam omnis praesentium sed. Rerum modi doloremque. Delectus aut sunt. Nulla cupiditate rerum ut debitis aut ipsa maxime voluptatem. Et aut voluptatem adipisci. Quam molestiae voluptate saepe. Sunt sint eum dolorem magni accusamus autem dolorem rem. Reiciendis voluptatem iste fugiat sapiente. Iure reiciendis mollitia perspiciatis alias distinctio magnam consequuntur. Magnam ad nihil fugiat qui et laboriosam et fugiat.",
        "hit": 562066,
        "category": {
            "id": 4
        },
        "user": {
            "id": 17
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2022-04-04T20:00:15.368Z",
        "publishedAt": "2022-04-12T02:06:32.308Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "ab5e3f6e-3e02-430f-9186-a3a70e9c684f",
                "status": "done",
                "type": "image/jpeg",
                "uid": "b242dbb2-1032-49ad-821a-4cec3911df50"
            }
        ],
        "tags": [
            6,
            8
        ],
        "language": 2
    },
    {
        "id": 959,
        "title": "Magni et eligendi.",
        "slug": "provident-modi-quia",
        "content": "Commodi repellendus eligendi. Fuga provident rerum. Aperiam et mollitia a. Dolorem fuga praesentium quia velit temporibus. Nobis quae ratione consequuntur. Occaecati voluptatem eius quis. Necessitatibus suscipit sed omnis sunt accusamus rerum odio eius ipsam. Non et at voluptas ut architecto officia. Recusandae fugiat officiis necessitatibus tenetur quis doloribus. Aut fuga recusandae consequatur.",
        "hit": 729432,
        "category": {
            "id": 5
        },
        "user": {
            "id": 2
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2022-05-24T20:21:21.871Z",
        "publishedAt": "2023-09-17T00:36:45.815Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "ec1fb507-c65a-4efe-8eae-c50e24b428d1",
                "status": "done",
                "type": "image/jpeg",
                "uid": "d95fa47b-5b18-4f95-9e06-e2970cb214d8"
            }
        ],
        "tags": [
            4,
            5,
            8
        ],
        "language": 2
    },
    {
        "id": 958,
        "title": "Dicta ut aliquam error voluptas sapiente maiores et vel et.",
        "slug": "et-id-quaerat",
        "content": "Sed accusantium suscipit et aliquid non. Id pariatur alias illo aut soluta doloremque sed officiis. Reiciendis incidunt ipsum qui. Quia alias consequuntur. Optio ea et. Maxime esse dolorem dolor ea error tempora pariatur ipsam deleniti. Autem qui voluptate ut exercitationem exercitationem et illum ea. Pariatur nesciunt rerum natus minima molestias beatae deserunt. Doloribus laborum laborum est velit quia consectetur. Dolores aut dolores maiores eius tempore minima id odit.",
        "hit": 570297,
        "category": {
            "id": 8
        },
        "user": {
            "id": 29
        },
        "status": "published",
        "status_color": "lime",
        "createdAt": "2023-08-24T13:30:12.760Z",
        "publishedAt": "2023-07-04T06:55:13.438Z",
        "image": [
            {
                "url": "http://loremflickr.com/640/480/abstract",
                "name": "110d290a-5742-4bd8-a071-810740b70f63",
                "status": "done",
                "type": "image/jpeg",
                "uid": "b90227ba-9803-4824-9878-a062bf4f0739"
            }
        ],
        "tags": [
            8,
            6
        ],
        "language": 3
    }
]

        # Créez la réponse JSON avec l'en-tête CORS approprié

        response = request.make_response(json.dumps(listEmployees))
        response.headers[
            'Access-Control-Allow-Origin'] = '*'  # Autorise toutes les origines (à adapter selon vos besoins)
        response.headers['Content-Type'] = 'application/json'

        return response

    # @http.route('/hr_soints/hr_soints/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('hr_soints.listing', {
    #         'root': '/hr_soints/hr_soints',
    #         'objects': http.request.env['hr_soints.hr_soints'].search([]),
    #     })

    # @http.route('/hr_soints/hr_soints/objects/<model("hr_soints.hr_soints"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('hr_soints.object', {
    #         'object': obj
    #     })