from flask import Flask, render_template, jsonify
from flask_restful import Api, Resource,reqparse

# Database ORM
from peewee import *

# Generate Database
db = "tes_va.db"
database = SqliteDatabase(db)

class BaseModel(Model):
	class Meta:
		database = database

class Transaction(BaseModel):
	id = AutoField(primary_key=True)
	payment = BooleanField(default=False)
	virtual_account = CharField(unique=True)

def create_tables():
	with database:
		database.create_tables([Transaction])

app = Flask(__name__)
api = Api(app)

# Resource Web Service
class Payment_notification(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument("va",type=str,required=True,help="Virtual Account Number, Must str, Required")
		args = parser.parse_args()

		va = args['va']

		# Check VA in DB
		try:
			cek_va = Transaction.get(Transaction.virtual_account == va)

			set_to_payed = Transaction.update(payment=True).where(Transaction.virtual_account == va)
			set_to_payed.execute()

			return jsonify({"hasil":"Terdeteksi Pembayaran di va {}".format(va),"status":"000"})

		except DoesNotExists:
			return jsonify({"hasil":"virtual account not found","status":"001"})

# Simple Read and Post some virtual_account Number
class read_and_post_va(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument("va",type=str, help="Virtual Account Number, Must str")
		args = parser.parse_args()

		if args['va'] is None:
			Data_Transaksi = []
			query_transaksi = Transaction.select()
			if query_transaksi.exists():
				for i in query_transaksi:
					data = {}
					data['id'] = i.id
					data['payment'] = i.payment
					data['virtual_account'] = i.virtual_account
					Data_Transaksi.append(data)
				return jsonify({"hasil":Data_Transaksi,'status':'000'})
			else:
				return jsonify({"hasil":Data_Transaksi,'status':'000'})
		else:
			Data_Transaksi = []
			query_transaksi = Transaction.select().where(Transaction.virtual_account == args['va'])
			if query_transaksi.exists():
				for i in query_transaksi:
					data = {}
					data['id'] = i.id
					data['payment'] = i.payment
					data['virtual_account'] = i.virtual_account
					Data_Transaksi.append(data)
				return jsonify({"hasil":Data_Transaksi,'status':'000'})
			else:
				return jsonify({"hasil":Data_Transaksi,'status':'000'})

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("va", type=str, required=True, help="Virtual Account Number, Must str, required")
		args = parser.parse_args()

		try:
			Transaction.create(virtual_account=args['va'])
			return jsonify({"hasil":"va {} Created".format(args['va']),"status":'000'})
		except IntegrityError:
			return jsonify({"hasil":"virtual_account already exists",'status':'001'})

api.add_resource(Payment_notification, "/api/payment")
api.add_resource(read_and_post_va, "/api/va")

if __name__ == "__main__":
	create_tables()
	app.run()