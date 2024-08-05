# if is_company:
#     query = (
#         select(CompanyAction, User, Company, CompanyMember)
#         .distinct()
#         .join(User, CompanyAction.user_id == User.id)
#         .join(Company, CompanyAction.company_id == Company.id)
#         .join(
#             CompanyMember,
#             and_(
#                 CompanyAction.company_id == CompanyMember.company_id,
#                 CompanyAction.user_id == CompanyMember.user_id,
#             ),
#         )
#         .filter(id_column == id_, CompanyAction.status == status)
#     )
# if not is_company:
#     query = (
#         select(CompanyAction, User, Company, CompanyMember)
#         .distinct()
#         .join(User, CompanyAction.user_id == User.id)
#         .join(Company, CompanyAction.company_id == Company.id)
#         .join(
#             CompanyMember, CompanyAction.company_id == CompanyMember.company_id
#         )
#         .filter(id_column == id_, CompanyAction.status == status)
#     )


# query = (
#     select(CompanyMember, CompanyAction, User, Company)
#     .join(Company, Company.id == CompanyMember.company_id)
#     .join(User, User.id == CompanyMember.user_id)
#     .join(
#         CompanyAction,
#         and_(
#             CompanyAction.company_id == Company.id,
#             CompanyAction.user_id == User.id,
#         ),
#     )
#     .filter(CompanyMember.company_id == company_id)
# )


# members_schemas = [
#     MembersResponseSchema(
#         id=member.CompanyMember.id,
#         user_id=member.CompanyMember.user_id,
#         company_id=member.CompanyMember.company_id,
#         action_id=member.CompanyAction.id,  # Extracting action_id from CompanyAction
#         company_name=await self.company_repository.get_company_name(
#             member.CompanyMember.company_id
#         ),
#         user_username=await self.user_repository.get_user_username(
#             member.CompanyMember.user_id
#         ),
#         role=await self.action_repository.get_member_role(
#             member.CompanyMember.user_id, member.CompanyMember.company_id
#         ),
#     )
#     for member in members
# ]
# return members_schemas
